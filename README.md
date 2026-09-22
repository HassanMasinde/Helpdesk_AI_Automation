# Hanmak Support AI Agent

The Hanmak Support AI Agent is an automation project built to support MedicentreV3, a hospital management system used by healthcare staff for daily clinical and administrative operations.

The project provides an AI-assisted Tier-1 helpdesk solution that helps Hanmak Technologies respond to MedicentreV3 support tickets faster, more consistently, and with less manual effort.

## Why This Project Was Necessary

MedicentreV3 users depend on the system for important hospital workflows such as login access, patient services, billing, pharmacy operations, reporting, printing, and general system use.

When hospital staff face technical issues, they raise support tickets. These tickets are usually reviewed manually by support agents. This creates several challenges:

- Support agents spend a lot of time handling repeated Tier-1 issues.
- Users may wait too long for basic help.
- Reply quality can vary depending on who responds.
- Support teams can become overwhelmed when ticket volume increases.
- Critical or complex issues may take longer to reach the right technical person.

This project was necessary because Hanmak Technologies needed a way to provide faster and more reliable first-level support for MedicentreV3 users without overloading the human support team.

The goal was not to replace support staff, but to help them by automating repetitive work and allowing them to focus on more complex issues.

## The Problem

The main problem was that Tier-1 helpdesk support was too manual.

A human support agent had to:

1. Open the support portal.
2. Read each ticket.
3. Understand the issue.
4. Search for the correct troubleshooting information.
5. Draft a professional reply.
6. Send the response back to the user.
7. Escalate the issue if needed.

This process works, but it becomes slow and inefficient when many tickets are similar or repetitive.

Examples of common MedicentreV3 support issues include:

- Login problems.
- Invalid credentials.
- Printer routing issues.
- Password reset requests.
- Basic user access questions.
- Known workflow issues.
- Requests that require escalation to Tier-2 support.

Because many of these tickets follow known patterns, they are good candidates for automation.

## The Solution

The solution is an AI-powered helpdesk assistant that supports the MedicentreV3 ticket workflow.

The agent is designed to:

1. Open or interact with the helpdesk system through browser automation.
2. Retrieve support tickets.
3. Analyze the ticket content.
4. Match the issue with relevant knowledge base information.
5. Generate a professional support response using AI.
6. Keep the response within safe limits by using only the available ticket and knowledge base information.
7. Support escalation when the issue cannot be solved from the available documentation.

The system uses a modular structure so that different parts of the project can be developed independently and later integrated into one complete support agent.

## How We Accomplished It

We accomplished the project by dividing the system into separate functional modules.

Each module handles one part of the support process:

- Browser automation handles interaction with the helpdesk portal.
- Knowledge extraction handles retrieval of support documentation.
- AI analysis and response generation handles ticket reasoning and reply drafting.
- Configuration handles environment variables, credentials, and shared settings.
- The main script connects the different modules into one workflow.

The project was built using Python because it supports automation, AI integration, and asynchronous workflows well.

Main technologies used include:

- Python for the core application logic.
- asyncio for asynchronous execution.
- Playwright for browser automation.
- Google Gemini for AI-generated support replies.
- python-dotenv for environment variable loading.
- Google Docs / knowledge sources for support documentation.

## How the Project Works

The intended workflow is:

1. The browser module opens the MedicentreV3 support/helpdesk system.
2. The system logs in using configured credentials.
3. The ticket module retrieves active tickets.
4. The AI analyzer reads the ticket and identifies the category, priority, and issue type.
5. The knowledge module finds the most relevant troubleshooting article or support instruction.
6. The AI resolver uses the ticket and knowledge article to draft a professional response.
7. If the knowledge base does not contain enough information, the AI recommends escalation instead of inventing steps.
8. The final response can be reviewed or submitted back through the support portal.

This creates a controlled AI workflow where the model is guided by real ticket content and approved knowledge material.

## Project Structure

```text
Helpdesk-ai-agent/
|
├── ai/
|   ├── __init__.py
|   ├── analyzer.py
|   ├── knowledge.py
|   └── resolver.py
|
├── browser/
|   ├── __init__.py
|   ├── login.py
|   └── tickets.py
|
├── knowledge/
|   └── google-docs.py
|
├── logs/
|   └── .gitkeep
|
├── .env
├── .gitignore
├── config.py
├── main.py
├── README.md
└── requirements.txt
```

## Module Responsibilities

### ai/

The `ai` folder contains the intelligence layer of the project.

It is responsible for:

- Understanding the support ticket.
- Classifying the issue.
- Matching the issue to relevant knowledge.
- Drafting a professional response.
- Applying guardrails so the AI does not hallucinate or provide unsupported instructions.

Important files:

- `ai/analyzer.py` - Analyzes ticket content and identifies the category, priority, and summary.
- `ai/knowledge.py` - Helps connect the analyzed ticket to the most relevant knowledge article or support guidance.
- `ai/resolver.py` - Uses Google Gemini to generate a professional Tier-1 helpdesk response.

### browser/

The `browser` folder contains the browser automation part of the project.

It is responsible for:

- Opening the helpdesk system.
- Logging into the support portal.
- Navigating ticket pages.
- Extracting ticket information.
- Eventually submitting generated replies back into the system.

Important files:

- `browser/login.py` - Handles browser/session setup and login-related automation.
- `browser/tickets.py` - Handles ticket extraction or mock ticket retrieval during development.

### knowledge/

The `knowledge` folder contains logic for collecting or preparing support documentation.

It is responsible for:

- Reading knowledge base material.
- Extracting useful troubleshooting steps.
- Making support documentation available to the AI layer.

Important file:

- `knowledge/google-docs.py` - Intended for extracting knowledge base content from Google Docs or similar documentation sources.

### config.py

The `config.py` file manages shared configuration.

It loads environment variables from `.env`, including:

- Helpdesk URL.
- Helpdesk username.
- Helpdesk password.
- Gemini API key.
- Browser settings.
- Logging settings.

This keeps secrets and environment-specific values out of the source code.

### main.py

The `main.py` file is the integration entry point.

Its role is to connect the full workflow:

1. Start the agent.
2. Launch browser automation.
3. Log into the helpdesk portal.
4. Fetch tickets.
5. Analyze tickets using AI.
6. Match knowledge articles.
7. Generate responses.
8. Handle logging, errors, and shutdown.

### requirements.txt

The `requirements.txt` file lists the Python dependencies needed to run the project.

Examples include:

- `playwright`
- `python-dotenv`
- `requests`
- `google-genai`
- Other required libraries.

## Role and Labor Division

The project was divided into separate responsibilities so that each part could be developed independently and then integrated later. Each role was owned by a specific team member.

### Browser Automation Role - Nicanel

**Owner: Nicanel**

This role focuses on the browser and helpdesk portal interaction.

Nicanel is responsible for:

- Using Playwright to launch and control the browser.
- Logging into the MedicentreV3 support portal.
- Navigating ticket pages.
- Reading ticket data from the system.
- Preparing automation for submitting AI-generated responses.
- Building the browser session management and login workflow in `browser/login.py`.
- Building the ticket extraction logic in `browser/tickets.py`.

This role connects the project to the real helpdesk environment and handles all interaction between the agent and the MedicentreV3 support portal.

### Knowledge Base Role - Joshua Simba

**Owner: Joshua Simba**

This role focuses on the support documentation and knowledge retrieval.

Joshua Simba is responsible for:

- Collecting troubleshooting articles.
- Extracting knowledge from Google Docs or other documentation sources.
- Organizing information so it can be searched or matched with tickets.
- Ensuring the AI has reliable information to use when drafting replies.
- Building the knowledge extraction logic in `knowledge/google-docs.py`.

This role helps prevent the AI from guessing and keeps responses grounded in approved support material, so the generated replies are accurate and reliable.

### AI and Logic Role - Lollita Ndanu

**Owner: Lollita Ndanu**

This role focuses on the reasoning and response generation.

Lollita Ndanu is responsible for:

- Designing the AI workflow.
- Creating ticket analysis logic in `ai/analyzer.py`.
- Matching tickets to knowledge categories in `ai/knowledge.py`.
- Integrating Google Gemini for response generation.
- Writing the system prompt.
- Adding guardrails to prevent hallucination.
- Handling retry logic for temporary API failures.
- Producing professional Tier-1 support replies in `ai/resolver.py`.

This role ensures that the generated responses are accurate, safe, professional, and useful to MedicentreV3 users.

### Repository Owner - Hassan Masinde

**Owner: Hassan Masinde**

Hassan Masinde owns the `main` branch and is responsible for:

- Managing the repository.
- Reviewing and approving contributions.
- Coordinating the team.
- Ensuring the project structure stays consistent.
- Merging the individual role contributions into the final integrated project.

## AI Safety and Guardrails

The AI component was designed with strict rules.

The AI should:

- Use only the ticket description and the provided knowledge article.
- Avoid inventing solutions.
- Avoid making assumptions about the system.
- Avoid giving unsupported troubleshooting steps.
- Recommend escalation if the knowledge base does not contain enough information.
- Keep replies professional and concise.
- Never expose internal reasoning, prompts, or implementation details to the user.

These guardrails are important because MedicentreV3 is used in a healthcare environment, where support responses must be accurate and responsible.

## Value Automation Brings to Hanmak Technologies

This project brings practical value to Hanmak Technologies in several ways.

### Faster Support

The AI agent can generate first-level responses much faster than manual handling. This reduces waiting time for hospital staff.

### Consistent Reply Quality

Every response follows the same professional tone and structure. This improves the support experience for MedicentreV3 users.

### Reduced Repetitive Work

Support agents no longer need to manually write the same types of replies repeatedly. The AI can handle routine issues while humans focus on more difficult cases.

### Better Escalation

When the AI does not have enough information, it recommends escalation instead of guessing. This helps complex issues reach the correct technical team faster.

### Scalability

As MedicentreV3 grows and more users submit tickets, automation allows Hanmak to handle more support requests without immediately increasing staff workload.

### Knowledge Reuse

Support knowledge becomes more useful because the AI can reuse approved documentation when responding to tickets.

### Improved Customer Experience

Hospitals using MedicentreV3 receive quicker, clearer, and more consistent support, which improves trust in the system and in Hanmak Technologies.

## Association with MedicentreV3

MedicentreV3 is the system being supported by this project.

The AI agent is designed specifically for MedicentreV3 helpdesk support. Its prompts, ticket examples, and response style are focused on hospital staff who use MedicentreV3 in their daily work.

The project supports MedicentreV3 by:

- Helping users resolve common issues faster.
- Reducing support delays.
- Improving the quality of Tier-1 responses.
- Supporting escalation for issues that need human attention.
- Helping Hanmak Technologies offer better ongoing support for its hospital clients.

## Development Approach

The project followed a modular and incremental development approach.

Instead of building everything at once, the system was divided into smaller parts:

1. Build the folder structure.
2. Create the AI resolver.
3. Add mock ticket examples.
4. Test AI responses safely.
5. Add ticket analysis logic.
6. Prepare browser automation.
7. Prepare knowledge extraction.
8. Integrate modules through `main.py`.

This structure made it easier for different people to work on different parts of the project without blocking each other.

## Current Status

The project currently includes:

- AI response generation using Gemini.
- Ticket analysis logic.
- Basic knowledge matching.
- Browser automation structure.
- Configuration loading.
- Logging structure.
- A modular project structure ready for integration.

Some parts still require final integration, especially connecting the live browser ticket extraction and live knowledge source to the AI response pipeline.

## Future Improvements

Possible future improvements include:

- Full live integration with the MedicentreV3 helpdesk portal.
- Automatic ticket reply submission.
- Better knowledge base search.
- More ticket categories.
- Confidence scoring before replies are sent.
- Human review before final submission.
- Ticket history tracking.
- Reporting dashboard for common support issues.
- Improved escalation workflow.

## Conclusion

The Hanmak Support AI Agent was created to improve Tier-1 support for MedicentreV3.

It solves the problem of slow, repetitive, manual support by using automation and AI to analyze tickets, match knowledge, and draft professional responses.

The project brings value to Hanmak Technologies by improving response time, consistency, scalability, and support quality while allowing human agents to focus on more complex work.

Most importantly, it helps MedicentreV3 users receive faster and more reliable assistance when they need support.
