# AppSec Bot Assistant

> **AI-powered AppSec assistant for Jira – smart comments, remediation help, and ticket updates.**

## Overview

The AppSec Bot Assistant is a GenAI-powered virtual Application Security engineer. It monitors Jira tickets for high-risk vulnerabilities, automatically comments on developer threads, provides remediation advice using OpenAI, and updates the ticket status, all in real-time or near real-time.

## Features

- Connects to Jira Cloud via REST API
- Auto-comments on high & critical vulnerability tickets
- Detects developer messages like "Need help with remediation" and responds using OpenAI
- Recognizes "This has been fixed" and moves ticket to `In Testing`
- Logs all ticket interactions and status changes
- (Stretch) Maintains a stateful chat log per ticket
- (Stretch) Summarizes final resolution in a closing comment

## Tech Stack

- **Python 3**
- **FastAPI** – API backend & optional dashboard
- **OpenAI API** – LLM-powered responses
- **Jira REST API** – ticket management
- **JSON / SQLite** – lightweight logging
- **Uvicorn** – FastAPI ASGI server

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/jaanvi-prabhakar/appsec-bot.git
cd appsec-bot
```

## File Structure

<pre>
├── main.py # FastAPI entry point
├── jira_handler.py # Jira API logic
├── llm_handler.py # OpenAI integration
├── state_manager.py # Chat memory (stretch)
├── templates/prompts.py # Prompt templates per vulnerability
├── logs/ticket_logs.json # JSON or SQLite logs
├── requirements.txt
└── README.md
</pre>

## Link to Demo Video

Coming soon
