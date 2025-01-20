# README - AI Customer Service & Sales Consulting Chatbot Backend (WhatsApp + OpenAI + Slack)

## Overview
This repository provides a Flask-based backend route (`/whatsapp`) that enables an AI-powered customer service and sales consulting chatbot through WhatsApp. The chatbot:

- Uses Twilio’s WhatsApp API to receive messages from end users.  
- Integrates with OpenAI’s Assistant API (the "Threads" and "Runs" concept) to process user messages and generate responses.  
- Optionally translates user messages or chatbot responses (via Google Translate, if desired).  
- Maintains thread IDs in Redis for fast lookup.  
- Posts interactions to Slack to notify human operators for tracking and live support.

**Key Use Case**:  
Multiple businesses can connect their WhatsApp business number. Each business maintains its own AI assistant (its own OpenAI "knowledge" or "direct instruction"), and end users interact with the chatbot over WhatsApp. Slack integration is used to view or jump into ongoing conversations if necessary.

---

## Table of Contents
1. [Architecture](#architecture)  
2. [Key Components](#key-components)  
3. [Setup and Installation](#setup-and-installation)  
4. [Configuration](#configuration)  
5. [Endpoint Behavior](#endpoint-behavior)  
6. [Redis and Thread Mapping](#redis-and-thread-mapping)  
7. [Slack Notifications](#slack-notifications)  
8. [Error Handling](#error-handling)  
9. [Known Limitations / Future Improvements](#known-limitations--future-improvements)  
10. [License](#license)  

---

## Architecture
### WhatsApp → Flask Endpoint
1. The user sends a WhatsApp message. Twilio forwards the message to our Flask route (`/whatsapp`).

### Thread Retrieval & Creation
1. The system looks up an existing conversation "thread" in Redis by the *(sender, receiver)* pair.  
2. If no thread is found, it checks the database for an existing `BusinessClient` record.  
3. If no database record is found, it creates a new thread in OpenAI and stores the details in both the database (async) and Redis.

### Chatbot Response via OpenAI
1. The user message is added to the conversation (`OpenAI beta.threads.messages`).  
2. A new "run" is triggered (`OpenAI beta.threads.runs`) to get the assistant’s reply.  
3. The system polls the run status until completion, retrieves the newest message from the assistant, and returns it to the user.

### Integration & Notifications
- Slack channels are created in the background for each new thread.  
- Customer messages and the AI responses are posted to Slack for human operator visibility.

### Return Response
- The final AI-generated message is sent back to the user via Twilio’s WhatsApp API.  
- The route returns an HTTP 200 success to confirm message delivery.

---

## Key Components

1. **Flask Blueprint**: `whatsapp_bp = Blueprint('whatsapp', __name__)`  
   - Houses the main `/whatsapp` POST endpoint.

2. **Redis**:  
   - Stores *(sender, receiver)* → `thread_id` mappings for fast thread lookups.

3. **PostgreSQL / SQLAlchemy Models**:  
   - `Business`, `BusinessClient`, `Client`, `Credentials`, `SlackUserIds` and more.  
   - `BusinessClient` associates a `business_id` with a `client_id` and the relevant `ai_thread`.

4. **OpenAI Thread & Run**:  
   - **Thread**: conversation context.  
   - **Run**: an inference request for each user message.

5. **Slack**:  
   - Slack channel creation for new threads.  
   - Posting user messages & AI responses in real time.

6. **Google Translate (optional)**:  
   - Potentially used to translate messages from or to a specific language (commented out in the final code).


## Environment Variables
You will likely need the following environment variables set (via `.env` or your hosting platform):

### OpenAI
- **OPENAI_API_KEY**  
- *(If using the Beta endpoints)* **OPENAI_BETA_BASE_URL** or any specialized environment variables

### Redis
- **REDIS_HOST** (e.g., `localhost`)  
- **REDIS_PORT** (e.g., `6379`)

### Slack
- **SLACK_BOT_TOKEN** (for posting messages and creating channels)

### Database
- **DATABASE_URL** or other custom config used by `config.py` and `models.py`

### Twilio
*(Depending on your Twilio integration method)*  
- **TWILIO_ACCOUNT_SID**  
- **TWILIO_AUTH_TOKEN**  
- Some config for the Twilio WhatsApp sender IDs or phone numbers

### Google Translate
- **GOOGLE_APPLICATION_CREDENTIALS** (if using GCP-based translation)  
- **TARGET_LANGUAGE** (if you want to specify which language to translate into)

---

## Additional Config Fields
- `business.is_disabled` flags can disable a business from processing user queries.  
- Slack channel naming or user IDs are stored in the `Business` and `SlackUserIds` relationship.


## Endpoint Behavior

### `POST /whatsapp`
Receives a JSON form submission (typical from Twilio) with these primary fields:

- **From**: The sender’s WhatsApp number (e.g., `"whatsapp:+123456789"`).
- **To**: The business’s WhatsApp number (e.g., `"whatsapp:+987654321"`).
- **Body**: The text message sent by the user.

#### Workflow

1. **Validate Incoming Message**  
   - Checks message length and ensures business is found & enabled in the database.

2. **Thread ID Lookup**  
   - Tries Redis first.  
   - If no match, queries the `BusinessClient` table.  
   - If not found, creates a new thread in OpenAI + Slack channel (async).

3. **Send User Message to OpenAI**  
   - Calls `openai_client.beta.threads.messages.create` to add the user message.

4. **Create Run**  
   - Triggers `create_run_with_timeout` to get the AI response.

5. **Check for Completion**  
   - Polls the run status in a loop until `'completed'` or `'failed'`.

6. **Retrieve Assistant Messages**  
   - Once done, fetches the latest assistant response from the `threads.messages` resource.

7. **Send WhatsApp Response**  
   - The final AI response is returned to the user’s WhatsApp through a `send_whatsapp_response()` function.

8. **Slack Notifications (in background threads)**  
   - Posts the user message + AI response to Slack.

9. **Response**  
   - On success, returns JSON `{"success": true}` with HTTP 200.  
   - On error, returns JSON `{"error": "..."}` with appropriate HTTP error codes.

---

## Redis and Thread Mapping

- **Redis Key**: `"{sender}_{receiver}" → { thread_id }`  
- Each conversation is stored as a hash:  
  ```bash
  HGETALL "whatsapp:+123456789_whatsapp:+987654321"
  # => { from: "...", to: "...", thread_id: "XXX" }


## Database

- **BusinessClient** table has `business_id`, `client_id`, `ai_thread`.
- If Redis doesn’t contain the mapping, the code looks for an existing `ai_thread` in **BusinessClient**.
- This cache–DB approach drastically speeds up repeated lookups.

---

## Slack Notifications

When a new thread is created:

1. **Create Slack Channel**  
   A dedicated Slack channel named something like `thread-{thread_id}` or a custom name.  
   The channel can then be used for asynchronous or real-time monitoring by team members.

2. **Post Messages**  
   - The user message + phone number is posted.  
   - The AI’s response is also posted.

Notifications are posted in background threads using Python’s `Thread` and `ThreadPoolExecutor`.

---

## Error Handling

1. **Internal Server Error (500)**  
   Returned if the code fails to create a thread, run, or retrieve messages from OpenAI after multiple attempts.

2. **Message Too Long (400)**  
   If `validate_message_length` fails, the route rejects the request.

3. **Business Disabled (403)**  
   If `business.is_disabled` is `True`, the route blocks user messages.

4. **Missing Business or Assistant (500)**  
   If we can’t map the inbound receiver phone number to a valid business or AI assistant.

Logs and tracebacks are printed to the console for debugging.
