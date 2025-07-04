from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
import logging

from fastapi.responses import HTMLResponse

from jira_handler import fetch_high_risk_tickets, get_comments, post_comment, transition_ticket_to_testing
from llm_handler import generate_remediation_response
from log_handler import log_event, get_logs

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
    "give a resolution",
    "recommed a resolution",
    "suggest a resolution",
    "please help",
    ]

FIXED_KEYWORDS = [
    "fixed",
    "resolved",
    "issue resolved",
    "this is fixed",
    "fix applied",
    "patch added",
    "vulnerability closed",
    "remediated",
    "solved"
]

KNOWN_VULNS = ["SQL Injection", "XSS", "Cross Site Scripting", "RCE", "Remote Code Execution", "Hardcoded Credentials", "Secrets", "CSRF", "Broken Auth", "IDOR"]

def should_trigger_llm(comment:str) -> bool:
    return any(kw in comment.lower() for kw in TRIGGER_KEYWORDS)

def extract_vuln_type(summary:str):
    for vuln in KNOWN_VULNS:
        if vuln.lower() in summary.lower():
            return vuln
    return "Unknown"

def is_marked_as_fixed(comment:str) -> bool:
    return any(keyword in comment.lower() for keyword in FIXED_KEYWORDS)

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
                # Post comment saying comments are being reviewed for high priority tickets
                already_posted = any (
                    "AppSec Bot is reviewing the comment" in comment for comment in existing_comments
                )
                if not already_posted:
                    message = "Hi team, AppSec Bot is reviewing the comment and will get back shortly..."
                    post_comment(ticket_id, message)
                    log_event(ticket_id, comment_type="initial")
                else:
                    logging.info(f"Skipping comment for ticket ID: {ticket_id}: already posted.")

                # Commenting a remediation suggestion, if not done already for the given ticket ID
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
                            log_event(ticket_id, comment_type="remediation")
                        else:
                            logging.info(f"Skipping remediation comment, already posted for ticket {ticket_id}")

                    # check if developer has marked the issue as fixed
                    if is_marked_as_fixed(comment):
                        logging.info(f"Detected 'fixed' status for ticket {ticket_id}, transitioning to 'In Testing'...")
                        transition_ticket_to_testing(ticket_id)
                        log_event(ticket_id, comment_type="fixed", status_transition="In Testing")

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

@app.get("/logs", response_class=HTMLResponse)
async def view_logs():
    logs = get_logs()
    
    html = """
    <html>
    <head>
        <title> AppSec Bot: Activity Log </title>
        <style>
            body { 
                font-family: Arial, 
                sans-serif; 
                padding: 20px; 
            }
            h2 { 
                color: #2c3e50; 
                margin-bottom: 2rem;
                margin-top: 2rem;
                text-align: center
            }
            table { 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 20px; 
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                overflow: hidden;
                border: 1px solid #ccc; 
            }
            td {
                background-color: #fffff;
            }
            th, td { 
                border: 1px solid #ccc; 
                padding: 8px 12px; 
                text-align: left; 
            }
            th { 
                background-color: #f2f2f2; 
            }
            tr:nth-child(even) { 
                background-color: #f9f9f9; 
            }
        </style>
    </head>
    <body>
        <h2>AppSec Bot:Activity Log</h2>
        <table>
            <tr>
                <th>Ticket</th>
                <th>Comment Type</th>
                <th>Status Transition</th>
                <th> Timestamp (UTC)</th>
            </tr>
    """

    badge_colors = {
        "initial": "#e3f2ff",
        "remediation": "#fff9db",
        "fixed": "#e6fae6"
    }

    for log in logs:
        formatted_time = datetime.fromisoformat(log['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        comment_type = log['comment_type'].lower()
        color = badge_colors.get(comment_type, "#e0e0e0")
        label = log['comment_type'].capitalize()

        html += f"""
        <tr>
            <td>{log['ticket_id']}</td>
            <td>
                <span style="background:{color};padding:2px 6px;border-radius:4px;">
                    {label}
                </span>
            </td>
            <td>{log.get('status_transition') or 'None'}</td>
            <td>{formatted_time}</td>
        </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    return HTMLResponse(content=html)