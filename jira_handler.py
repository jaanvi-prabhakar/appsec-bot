from urllib import response
from httpx import head
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

AUTH = (JIRA_EMAIL, JIRA_API_TOKEN)

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