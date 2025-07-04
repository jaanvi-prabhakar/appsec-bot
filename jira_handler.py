import json
import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")

JIRA_BASE_URL = f"http://{JIRA_DOMAIN}/rest/api/3"

HEADERS = {
    "Accept" : "application/json",
    "Content-Type": "application/json"
}

if not JIRA_EMAIL or not JIRA_API_TOKEN:
    raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN must be set in .env")
AUTH: tuple[str, str] = (JIRA_EMAIL, JIRA_API_TOKEN)

# JQL query to get open tickets with risk=High or Critical
JQL_QUERY = 'statusCategory = "To Do" AND labels IN ("High", "Critical") ORDER BY created DESC'

def fetch_high_risk_tickets():
    url = f"{JIRA_BASE_URL}/search"
    params = {
        "jql" : JQL_QUERY,
        "maxResults": 10
    }

    try:
        response = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
        response.raise_for_status()
        issues = response.json().get("issues", [])
        logging.info(f"Fetched {len(issues)} Jira tickets.")
        return issues
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Jira tickets: {e}")
        return []
    
def get_comments(ticket_id:str):
    """
    Fetch existing comments on a given Jira ticket.

    Args:
        ticket_id(str): The Jira issue key (ex. "KAN-1")

    Returns:
        List of comment bodies
    """

    url=f"{JIRA_BASE_URL}/issue/{ticket_id}/comment"
    
    try:
        response = requests.get(url, headers=HEADERS, auth=AUTH)
        response.raise_for_status()
        comments = response.json().get("comments", [])

        # extract plain text from ADF - atlassian document format body
        extracted_comments = []
        for comment in comments:
            text = ""
            for block in comment["body"].get("content", []):
                for inline in block.get("content", []):
                    text += inline.get("text", "")
            extracted_comments.append(text)
            logging.info(extracted_comments)
        return extracted_comments
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get comments for ticket ID: {ticket_id} due to error: {e}")
        return []

    
def post_comment(ticket_id: str, message:str):
    """
    Posts a comment to a specific Jira issue.

    Args:
        ticket_id(str): The Jira issue key (e.g., "KAN-1")
        message(str): The comment text to post
    """

    url = f"{JIRA_BASE_URL}/issue/{ticket_id}/comment"
    payload = {
        "body" : {
            "type": "doc",
            "version": 1,
            "content" : [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(url, headers=HEADERS, auth=AUTH, json=payload)
        response.raise_for_status()
        logging.info(f"Comment posted to ticket_id: {ticket_id}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to post comment to {ticket_id}: {e}")

def get_transitions(ticket_id: str):
    url = f"{JIRA_BASE_URL}/issue/{ticket_id}/transitions"
    try:
        response = requests.get(url, headers=HEADERS, auth=AUTH)
        response.raise_for_status()
        transitions = response.json()
        print(json.dumps(transitions, indent=2))
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get transactions for {ticket_id}: {e}")

def transition_ticket_to_testing(ticket_id: str) -> None:
    """
    Moves the Jira ticket to 'In Testing' status.

    Args:

    """
    #Created a new state and column of "In Testing" on the JIRA Board

    url = f"{JIRA_BASE_URL}/issue/{ticket_id}/transitions"
    payload = {
        "transition" : {
            "id" : "2" # Got id of 'In Testing' from browser dev tools & test_transitions.py
        }
    }

    try:
        response = requests.post(url, json=payload, headers=HEADERS, auth=AUTH)
        response.raise_for_status()
        logging.info(f"Ticket {ticket_id} successfully moved to 'In Testing'")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to transition {ticket_id} to 'In Testing'")