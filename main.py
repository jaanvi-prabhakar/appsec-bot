from contextlib import asynccontextmanager
from email import message
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
import logging

from jira_handler import fetch_high_risk_tickets, get_comments, post_comment
from llm_handler import generate_remediation_response

# load env variables
load_dotenv()

# set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

#Constants
POLL_INTERVAL = 60

# define words that trigger LLM
TRIGGER_KEYWORDS = [
    "remediation", 
    "remediate this",
    "need help", 
    "can you help",
    "how to fix", 
    "suggest fix", 
    "suggest a fix",
    "how can i fix", 
    "help me fix",
    "fix this",
    "need fix",
    "need a fix",
    "what's the fix",
    "help me resolve",
    "how can i resolve",
    "how do i resolve",
    "resolve this",
    "need resolution",
    "need a resolution",
    "recommend fix",
    "any suggestions",
    "give resolution",
    "give a resolution"
    "recommed a resolution",
    "suggest a resolution",
    "please help"
    ]

KNOWN_VULNS = ["SQL Injection", "XSS", "Cross Site Scripting", "RCE", "Remote Code Execution", "Hardcoded Credentials", "Secrets", "CSRF", "Broken Auth", "IDOR"]

def should_trigger_llm(comment:str) -> bool:
    return any(kw in comment.lower() for kw in TRIGGER_KEYWORDS)

def extract_vuln_type(summary:str):
    for vuln in KNOWN_VULNS:
        if vuln.lower() in summary.lower():
            return vuln
    return "Unknown"

#Lifespan manager
@asynccontextmanager
async def lifespan(app:FastAPI):
    async def poll_tickets():
        while True:
            logging.info("Polling Jira tickets...")

            # calling Jira handler here
            tickets = fetch_high_risk_tickets()

            for ticket in tickets:
                ticket_id = ticket["key"]
                summary = ticket["fields"]["summary"]
                logging.info(f"Ticket ID: {ticket_id} | Summary: {summary}")

                #check for existing comments
                existing_comments = get_comments(ticket_id)

                already_posted = any (
                    "AppSec Bot is reviewing the comment" in comment for comment in existing_comments
                )
                if not already_posted:
                    message = "Hi team, AppSec Bot is reviewing the comment and will get back shortly..."
                    post_comment(ticket_id, message)
                else:
                    logging.info(f"Skipping comment for ticket ID: {ticket_id}: already posted.")

                already_posted_remediation = any (
                    "Remediation suggestion:" in comment for comment in existing_comments
                )

                # check latest comments for remediation request
                for comment in existing_comments:
                    if should_trigger_llm(comment) and "AppSec Bot" not in comment:
                        if not already_posted_remediation:
                            logging.info(f"Detected remediation request for ticket: {ticket_id}")
                            
                            vuln_type = extract_vuln_type(summary)
                            logging.info(f"Extracted vulnerability type: {vuln_type} from summary: {summary}")

                            remediation = generate_remediation_response(vuln_type, summary)
                            bot_reply = f"Remediation suggestion:\n\n{remediation}"
                            post_comment(ticket_id, bot_reply)
                        else:
                            logging.info(f"Skipping remediation comment, already posted for ticket {ticket_id}")

            await asyncio.sleep(POLL_INTERVAL) # poll every 60s

    asyncio.create_task(poll_tickets())

    yield # wait here until shutdown

    #shutdown logic
    logging.info("App is shutting down.")

app = FastAPI(title="AppSec Bot Assistant", lifespan=lifespan)

# CORS for front end dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route
@app.get("/ping")
async def ping():
    return {"message": "AppSec Bot is running"}