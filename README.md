# DuelBot - Discord Bot

A modular Discord bot built with Python and discord.py, featuring a clean architecture and organized codebase.

## Project Structure

```
DuelBot/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Main entry point
│   ├── bot.py               # Main bot class
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and operations
│   ├── events.py            # Event handlers
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   ├── user.py          # User and UserStats models
│   │   └── duel.py          # Duel and DuelMove models
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── database_service.py  # Database operations
│   │   ├── user_service.py      # User business logic
│   │   └── duel_service.py      # Duel business logic
│   ├── controllers/         # Command handlers (like routes)
│   │   ├── __init__.py
│   │   ├── duel_controller.py   # Duel command handlers
│   │   └── user_controller.py   # User command handlers
│   ├── middleware/          # Common functionality
│   │   ├── __init__.py
│   │   ├── cooldown_middleware.py  # Cooldown management
│   │   └── error_middleware.py     # Error handling
│   ├── utils/               # Helper functions
│   │   ├── __init__.py
│   │   ├── helpers.py       # Utility functions
│   │   └── validators.py    # Validation functions
│   └── commands/            # Discord command definitions
│       ├── __init__.py
│       ├── basic.py         # Basic commands
│       ├── admin.py         # Admin commands
│       └── duel_commands.py # Duel system commands
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a Discord Application:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to the "Bot" section
   - Click "Add Bot"
   - Copy the bot token

3. **Set up PostgreSQL database:**
   - Install PostgreSQL on your system
   - Create a database named `duelbot`
   - Note your database credentials

4. **Configure the bot:**
   - Create a `.env` file in the project root
   - Add your bot token and database configuration:
     ```env
     DISCORD_BOT_TOKEN=your_actual_bot_token_here
     COMMAND_PREFIX=$
     BOT_NAME=DuelBot
     BOT_ACTIVITY=for duels
     LOG_LEVEL=INFO
     
     # Database Configuration
     DATABASE_URL=postgresql://username:password@localhost:5432/duelbot
     DB_HOST=localhost
     DB_PORT=5432
     DB_NAME=duelbot
     DB_USER=your_db_username
     DB_PASSWORD=your_db_password
     
     # Duel Settings
     DUEL_COOLDOWN=300
     DUEL_TIMEOUT=60
     MAX_DUEL_DURATION=300
     ```

4. **Invite the bot to your server:**
   - In the Discord Developer Portal, go to OAuth2 > URL Generator
   - Select "bot" scope
   - Select necessary permissions (Send Messages, Read Message History, etc.)
   - Use the generated URL to invite the bot

5. **Run the bot:**
   ```bash
   python src/main.py
   ```

## Commands

### Duel Commands
- `$duel @user` - Challenge a user to a duel
- `$accept` - Accept a pending duel challenge
- `$decline` - Decline a pending duel challenge
- `$cancel` - Cancel your pending duel challenge
- `$attack` - Attack your opponent in an active duel
- `$defend` - Defend (reduces incoming damage)
- `$heal` - Heal yourself in an active duel
- `$special` - Use special attack (risky but powerful)
- `$duelstatus` - Check your current duel status

### User Commands
- `$profile [@user]` - View your or another user's profile
- `$stats [@user]` - View stats (alias for profile)
- `$leaderboard [limit]` - View the guild leaderboard

### Basic Commands
- `$ping` - Check bot latency
- `$hello` - Say hello to the bot
- `$info` - Get bot information
- `$help` - Show help message
- `$help <command>` - Show help for specific command

### Admin Commands (Owner Only)
- `$shutdown` - Shutdown the bot
- `$reload <module>` - Reload a command module
- `$guilds` - List all guilds the bot is in
- `$status <type> <text>` - Set bot status (playing/watching/listening/streaming)

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Configuration Management**: Environment-based configuration
- **Comprehensive Logging**: Structured logging with configurable levels
- **Error Handling**: Robust error handling for commands and events
- **Rich Embeds**: Beautiful embed responses for commands
- **Admin Tools**: Owner-only administrative commands
- **Extensible**: Easy to add new commands and features

## Development

### Adding New Commands

1. Create a new file in `src/commands/` (e.g., `src/commands/games.py`)
2. Define your commands with proper error handling
3. Add the setup function to `src/commands/__init__.py`
4. The commands will be automatically loaded

### Adding New Events

1. Add event handlers to `src/events.py`
2. Events are automatically registered when the bot starts

### Configuration

All configuration is managed through environment variables in the `.env` file. See `src/config.py` for available options.

## License

This project is open source and available under the MIT License.
