from http import client
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# load env variables
load_dotenv()

# Using OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_remediation_response(vuln_type: str, description: str) -> str:
    """
    Generates a remidiation suggestion using OpenAI based on vulnerability type and description.

    Args:
        vuln_type (str): Type of vulnerability (ex. SQLi, XSS, Secrets)
        description (str): Developer's comment or context

    Returns:
        str: AI-generated remediation advice 
    """

    system_prompt = f"You are an expert Application Security engineer. Help developers remediate {vuln_type} vulnerabilities."
    user_prompt = f"Vulnerability type: {vuln_type}\n Issue description: {description}\n What is the recommended remediation?"

    try:
        response = client.chat.completions.create (
            model="gpt-3.5-turbo",
            messages= [
                {"role":"system", "content": system_prompt},
                {"role":"user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=300,
        )
        message = response.choices[0].message.content
        reply = message.strip() if message else "Sorry, no response was returned."
        logging.info("LLM Remediation response is generated.")
        return reply
    
    except Exception as e:
        logging.error(f"Failed to generate remediation response: {e}")
        return "Sorry, AppSec Bot is unable to generate a remediation suggestion at the moment"

