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
│   ├── events.py            # Event handlers
│   └── commands/
│       ├── __init__.py      # Commands package
│       ├── basic.py         # Basic commands
│       └── admin.py         # Admin commands
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

3. **Configure the bot:**
   - Create a `.env` file in the project root
   - Add your bot token and any other configuration:
     ```env
     DISCORD_BOT_TOKEN=your_actual_bot_token_here
     COMMAND_PREFIX=!
     BOT_NAME=DuelBot
     BOT_ACTIVITY=for commands
     LOG_LEVEL=INFO
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

### Basic Commands
- `!ping` - Check bot latency
- `!hello` - Say hello to the bot
- `!info` - Get bot information
- `!help` - Show help message
- `!help <command>` - Show help for specific command

### Admin Commands (Owner Only)
- `!shutdown` - Shutdown the bot
- `!reload <module>` - Reload a command module
- `!guilds` - List all guilds the bot is in
- `!status <type> <text>` - Set bot status (playing/watching/listening/streaming)

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
