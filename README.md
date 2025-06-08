# Roleplay Chat Bot

A Telegram bot for immersive roleplaying experiences powered by Google's Gemini AI, using SQLite for local data storage.

## Key Features

- **AI-Powered Roleplaying**: Utilizes Google's `gemini-2.0-flash` model for dynamic responses
- **Character Management**:
  - Store custom characters in local database
  - Manage user personas (roleplay profiles)
- **Privacy Focused**:
  - No chat history storage
  - Each session starts fresh

## Technical Stack

- **AI Provider**: Google Generative AI API
- **Backend**: Python 3.12.3 with aiogram (Async Telegram Bot Framework)
- **Database**:
  - SQLite via aiosqlite (async)
  - SQLAlchemy ORM for data models

## Setup Instructions

1. Create `.env` configuration file:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   DATABASE_URL=sqlite+aiosqlite:///db.sqlite3
   DEBUG_MODE=true
2. Install required dependencies:
   ```env
   pip install -r requirements.txt
3. Launch the bot:
   ```env
   python3 main.py

## Usage Guide
1. Initiate the bot with `/start` command

2. Use Options menu to:
- Create and manage characters
- Set up and manage user personas

3. Select active character and persona before starting

4. Begin roleplaying by sending any message

5. Start the chat anew with New Chat menu option

6. Check your active characters and personas with `/status` command

## Database Information
- The application utilizes a local SQLite database (db.sqlite3) with:
- Simple relational schema (users, characters, personas)
- Asynchronous database access via aiosqlite
- No conversation history storage

Note: All character and persona data is stored exclusively in the local SQLite database file.
