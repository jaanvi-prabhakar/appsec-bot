import openai
from dotenv import load_dotenv
import logging

# load env variables
load_dotenv()

def generate_remediation_response(vuln_type: str, description: str) -> str:
    """
    Generates a remediation suggestion using OpenAI based on vulnerability type and description.

    Args:
        vuln_type (str): Type of vulnerability (ex. SQLi, XSS, Secrets)
        description (str): Developer's comment or context

    Returns:
        str: AI-generated remediation advice 
    """

    REMEDIATION_PROMPT_TEMPLATE = """
    You are an expert Application Security engineer.
    A Jira ticket reports a vulnerability of type {vuln_type}.
    Write a concise and actionable remediation suggestion for developers. 
    Use Jira-style markdown (such as bullet points, numbered steps, code blocks) for formatting if helpful. Do not use bold or italics.
    
    Ensure the guidance follows best practices, includes code level recommendations (if applicable) and any prevention tips.

    Output only the remediation suggestion, no extra introductions or summaries.
    """

    system_prompt = REMEDIATION_PROMPT_TEMPLATE;
    user_prompt = (
        f"Vulnerability type: {vuln_type}\n"
        f"Issue description: {description}\n" 
        "Please provide the recommended remediation steps."
    )

    try:
        response = openai.chat.completions.create (
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

