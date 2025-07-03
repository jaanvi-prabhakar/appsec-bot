from contextlib import asynccontextmanager
from email import message
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
import logging

from jira_handler import fetch_high_risk_tickets, get_comments, post_comment

# load env variables
load_dotenv()

# set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

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

            await asyncio.sleep(60) # poll every 60s

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