# Telegram Scraper Skills

Agent skills for extracting content from Telegram channels (public, private, paywalled).

## Skills

| Skill | Description |
|-------|-------------|
| `telegram-scraper` | Extract content from Telegram channels via web scraping, Telethon API, or manual exports |

## Features

- **Public channels**: Web scraping via Playwright (no login required)
- **Private channels**: Telethon API or Playwright with login
- **Paywalled channels**: Manual export via Telegram Desktop
- **Bulk extraction**: Process multiple Telegram Desktop exports

## Installation

```bash
# Copy skills to your agent's skills directory
cp -r skills/* ~/.agents/skills/

# For OpenCode/Codex
cp -r skills/* ~/.agents/skills/
```

## Prerequisites

| Method | Requirements |
|--------|--------------|
| Web scraping | `npx playwright-cli` |
| Telethon API | `pip install telethon` |
| Manual export | Telegram Desktop |

## Quick Start

### Public Channel (Web Scraping)

```bash
npx playwright-cli open "https://t.me/s/CHANNEL_NAME"
npx playwright-cli eval "document.body.innerText"
```

### Telegram Desktop Export

1. Open Telegram Desktop
2. Settings → Advanced → Export Telegram data
3. Select channel and export as JSON
4. Run `scripts/extract_all_chats.py` to process

## License

MIT