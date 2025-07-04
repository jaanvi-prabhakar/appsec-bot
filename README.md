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

## Screenshots

### Tickets Created + Initial Steps

![Tickets Created](outputs/tickets_created.png)
![JIRA Board](outputs/JIRA_board.png)

### Remediation Outputs: for tickets marked with high or critical label

![Login API SQL Injection Remediation](outputs/login_sql_injection_remediation.png)
![XSS Vuln Remediation](outputs/xss_vuln_remediation.png)
![No Critical Labels](outputs/debugging/no_trigger_label.png)
![No Critical Labels](outputs/debugging/no_trigger_label_2.png)
![Hardcoded AWS Credentials Remediation](outputs/hardcoded_creds_remediation.png)
![Admin Reports SQL Injection Remediation](outputs/admin_reports_sql_injection_remediation.png)

### Fixed → In Testing

![Fixed to Testing](outputs/fixed_ticket_moved_to_testing.png)

### Logs Dashboard

![Logs](outputs/logging_web_dashboard.png)

## Link to Demo Video

Coming soon
