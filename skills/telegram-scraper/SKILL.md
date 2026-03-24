---
name: telegram-scraper
description: Extract content from Telegram channels (public, private, paywalled). Use this skill when the user wants to scrape Telegram channels, extract chat history, download messages from Telegram, or says "scrape Telegram", "get Telegram content", "extract from t.me". Supports public channels via web scraping, private channels via Telethon API, and manual export via Telegram Desktop.
license: Complete terms in LICENSE.txt
---

# Telegram Channel Scraper

Extract content from Telegram channels (public, private, paywalled).

## Channel Types

| Type | Access Method | Requirements |
|------|---------------|--------------|
| Public | Tavily extract (Method 1) | None (URL only) |
| Public | Playwright (Method 2) | `npx playwright-cli` |
| Private | Telethon API (Method 3) | api_id, api_hash, phone |
| Private | Playwright + login (Method 4) | User logs in manually |
| Paywalled | Browser + session (Method 4) | Account + subscription |
| Any | Manual export (Method 5) | Telegram Desktop |

## Workflow

Follow this escalation pattern:

1. **Try Tavily extract** — `tvly extract "https://t.me/s/CHANNEL_NAME"` (Method 1)
2. **Failed?** → Use Playwright web scraping (Method 2)
3. **Private?** → Use Telethon API (Method 3) or Playwright with login (Method 4)
4. **Paywalled?** → Manual export via Telegram Desktop (Method 5)

## Method 1: Tavily Extract (Public Channels - Simplest)

Best for: Public channels, quick extraction without setup

```bash
# Extract content from public preview page
tvly extract "https://t.me/s/CHANNEL_NAME" --format markdown
```

**Limitations:**
- May get garbled content (JS rendering issues)
- Rate limited by Telegram
- Use Playwright (Method 2) if this fails

## Method 2: Playwright Web Scraping (Public Channels - Reliable)

Best for: Public channels when Method 1 fails, JS-rendered content

```bash
# Navigate to channel web preview
npx playwright-cli open "https://t.me/s/CHANNEL_NAME"

# Extract text content
npx playwright-cli eval "document.body.innerText"

# Take snapshot for DOM analysis
npx playwright-cli snapshot
```

**URL Pattern:**
- Full: `https://t.me/CHANNEL_NAME` (requires login for full content)
- Preview: `https://t.me/s/CHANNEL_NAME` (public preview, no login)

**DOM Selectors:**
```css
.tgme_widget_message        /* Message container */
.tgme_widget_message_text   /* Message text */
.tgme_widget_message_views  /* View count */
.time                       /* Timestamp */
.tgme_widget_message_photo_wrap  /* Image link */
```

## Method 3: Telethon API (All Channels)

Best for: Private channels, bulk extraction, media

**Setup:**
1. Get api_id and api_hash from https://my.telegram.org/apps
2. Install: `pip install telethon`
3. Run with phone number authentication

```python
from telethon import TelegramClient

api_id = YOUR_API_ID
api_hash = 'YOUR_API_HASH'

async def scrape_channel(client, channel_username, limit=100):
    async with client:
        channel = await client.get_entity(channel_username)
        messages = await client.get_messages(channel, limit=limit)
        for msg in messages:
            if msg.text:
                print(f"{msg.date}: {msg.text}")
```

## Method 3: Telegram Desktop Export (Any Channel)

Best for: Private/paywalled channels, complete history, no coding

**Steps:**
1. Open Telegram Desktop
2. Settings → Advanced → Export Telegram data
3. Select channel/chat to export
4. Choose format: JSON or HTML
5. Select what to export: messages, media, files
6. Export to chosen directory

**Output:**
```
ChatExport_YYYY-MM-DD/
├── result.json          # All messages in JSON
├── video_files/         # Downloaded videos
├── stickers/            # Sticker files
└── files/               # Other files
```

## Method 4: Playwright with Login (Private/Closed Channels)

Best for: Private/closed channels requiring login, persistent session

```bash
# Open Telegram Web in headed mode - user will log in manually
npx playwright-cli open "https://web.telegram.org/" --headed

# >>> USER ACTION: Log in manually in the browser window <<<
# Wait for user confirmation, then:

# Search for channel
npx playwright-cli type "CHANNEL_NAME"

# Click on channel in search results (use ref from snapshot)
npx playwright-cli click eREF

# Extract content
npx playwright-cli eval "document.querySelectorAll('.tgme_widget_message_text').length + ' messages'"

# Scroll for more content
npx playwright-cli press End
npx playwright-cli eval "document.body.innerText"

# Navigate to next channel (browser stays open!)
npx playwright-cli go-back  # Return to chat list
npx playwright-cli type "OTHER_CHANNEL"
npx playwright-cli click eREF
```

**Workflow:**
1. Agent opens Telegram Web in headed mode
2. **User logs in manually** (browser window visible)
3. Agent navigates to target channel
4. Agent extracts content
5. **Browser stays open** — agent can navigate to next channel
6. Repeat for multiple channels without re-login

**For open channels via preview:**
```bash
# Open channel preview (no login needed for public channels)
npx playwright-cli open "https://t.me/s/CHANNEL_NAME"

# Extract messages
npx playwright-cli eval "document.querySelector('.tgme_widget_message_text').innerText"
```

**Session Management:**
- Browser session persists between extractions
- Use `go-back` to return to chat list
- Use `tab-list` / `tab-select` if needed
- No need to close/reopen browser between scrapes

**DOM Selectors for Telegram Web:**
```css
.tgme_widget_message_text   /* Message text (preview pages) */
.chat-list-item             /* Chat in sidebar */
.message                    /* Message container */
.time                       /* Timestamp */
```

## Method 5: Telethon API (All Channels)

Best for: Private channels, bulk extraction, media, programmatic access

**Setup:**
1. Get api_id and api_hash from https://my.telegram.org/apps
2. Install: `pip install telethon`
3. Run with phone number authentication

```python
from telethon import TelegramClient

api_id = YOUR_API_ID
api_hash = 'YOUR_API_HASH'

async def scrape_channel(client, channel_username, limit=100):
    async with client:
        channel = await client.get_entity(channel_username)
        messages = await client.get_messages(channel, limit=limit)
        for msg in messages:
            if msg.text:
                print(f"{msg.date}: {msg.text}")
```

## Script: Extract All Chat Exports

**Location:** `scripts/extract_all_chats.py`

**Purpose:** Extract all text content from Telegram Desktop chat exports (JSON format).

**Usage:**
```bash
# Run from any directory
python scripts/extract_all_chats.py
```

**What it does:**
- Scans export directories for `result.json` files
- Extracts: message text, sender, date, media type, forwarded info
- Handles corrupted JSON with partial parsing
- Outputs: `CHANNEL_NAME_full.md` files

**Output:**
- Per-channel markdown files with all text messages
- Summary statistics (total messages, text messages)

## Output Format

Save extracted content to:
```
D:/Documents/cmw-rag-channel-extractions/CHANNEL_NAME.md
```

**Format:**
```markdown
# @CHANNEL_NAME

Source: https://t.me/CHANNEL_NAME
Date: YYYY-MM-DD
Subscribers: X

---

## Entry 1 - Date

[Message content]

---

## Key Topics

- Topic 1
- Topic 2
```

## Tips

- Use `--disable-images` to speed up scraping
- Scroll to load more messages (infinite scroll)
- Handle rate limiting with delays
- **Session persists** — browser stays open between scrapes
- Use `go-back` to return to chat list
- Use `state-save` to persist session for future sessions
- Export to JSON for structured data processing
- Manual export is most reliable for private channels

## See Also

- [Telethon Docs](https://docs.telethon.dev/)
- [Playwright Skill](../playwright-cli/SKILL.md)
- [Apify Telegram Scraper](https://apify.com/apify/telegram-channels-scraper)
- [Telegram Desktop](https://desktop.telegram.org/)