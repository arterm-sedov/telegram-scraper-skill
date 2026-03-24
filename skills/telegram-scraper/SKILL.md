---
name: telegram-scraper
description: Extract TEXT content from Telegram channels (public, private, paywalled). Use this skill when the user wants to scrape Telegram channels, extract chat history, download messages from Telegram, or says "scrape Telegram", "get Telegram content", "extract from t.me". Focus on text extraction - OCR/vision only for browser automation (clicking, searching).
license: Complete terms in LICENSE.txt
---

# Telegram Channel Scraper

Extract **TEXT content** from Telegram channels (public, private, paywalled).

**Important:** Always extract text via DOM/JSON. OCR/vision is ONLY for browser automation (clicking buttons, entering search queries), never for content extraction.

## Channel Types

| Type | Method | Requirements |
|------|--------|--------------|
| Public | Playwright preview | `npx playwright-cli`, no login |
| Private/Closed | Playwright headed + user login | User logs in once, session persists |
| Any | Desktop Export + Script | Telegram Desktop, then run script |

## OCR/Vision Usage

**Only for browser automation:**
- Clicking buttons (login, search, navigate)
- Entering text in search fields
- Finding elements by visual reference

**Never for content extraction:**
- Message text → Use DOM selectors
- Message metadata → Use DOM selectors
- Export data → Use JSON parsing

## Method 1: Public Channels (Playwright Preview)

For public channels, use the preview URL (no login needed):

```bash
# Open channel preview
npx playwright-cli open "https://t.me/s/CHANNEL_NAME"

# Extract message count
npx playwright-cli eval "document.querySelectorAll('.tgme_widget_message_text').length"

# Extract first message text
npx playwright-cli eval "document.querySelector('.tgme_widget_message_text').innerText"

# Extract all messages as array (first 5)
npx playwright-cli eval "Array.from(document.querySelectorAll('.tgme_widget_message_text')).slice(0,5).map(el => el.innerText).join('\\n---\\n')"
```

**URL Pattern:**
- Preview: `https://t.me/s/CHANNEL_NAME` (public, no login)
- Full: `https://t.me/CHANNEL_NAME` (may require login)

**DOM Selectors:**
```css
.tgme_widget_message_text   /* Message text - USE THIS */
.tgme_widget_message        /* Message container */
.tgme_widget_message_views  /* View count */
.time                       /* Timestamp */
```

## Method 2: Private/Closed Channels (Playwright Headed + Login)

For private/closed channels, start a headed browser session and ask user to log in:

```bash
# 1. Open Telegram Web in headed mode
npx playwright-cli open "https://web.telegram.org/" --headed

# 2. >>> ASK USER: "Please log in to Telegram in the browser window" <<<

# 3. Wait for user confirmation, then use OCR/vision to navigate:
npx playwright-cli snapshot
# Use OCR to find search box, click it
npx playwright-cli click eREF

# 4. Type channel name (use OCR to find input field)
npx playwright-cli type "CHANNEL_NAME"

# 5. Click on channel in results
npx playwright-cli click eREF

# 6. Extract TEXT content (DOM, not OCR!)
npx playwright-cli eval "document.querySelectorAll('.message').length"

# 7. Keep browser open for subsequent channels
npx playwright-cli go-back
# Repeat from step 3 for next channel
```

**Key Points:**
- **User logs in ONCE** - session persists
- **Browser stays open** - no need to re-login
- **Use DOM for text extraction** - never OCR
- **Use OCR/vision only** for clicking buttons/inputs

**DOM Selectors for Telegram Web:**
```css
.message                    /* Message container */
.text-content               /* Message text */
.chat-list-item             /* Chat in sidebar */
.time                       /* Timestamp */
```

## Method 3: Telegram Desktop Export (Any Channel)

For any channel, export via Telegram Desktop:

**Steps:**
1. Open Telegram Desktop
2. Settings → Advanced → Export Telegram data
3. Select channel/chat to export
4. Choose format: **JSON** (preferred for text extraction)
5. Select: messages (skip media for speed)
6. Export to directory

**Output:**
```
ChatExport_YYYY-MM-DD/
├── result.json          # All messages in JSON
├── video_files/         # Downloaded videos
├── stickers/            # Sticker files
└── files/               # Other files
```

**Process exports:**
```bash
python scripts/extract_all_chats.py
```

## Script: extract_all_chats.py

**Location:** `scripts/extract_all_chats.py`

**Purpose:** Parse Telegram Desktop JSON exports into markdown.

**Usage:**
```bash
python scripts/extract_all_chats.py
```

**What it does:**
- Scans export directories for `result.json` files
- Extracts: message text, sender, date, media type, forwarded info
- Handles corrupted JSON with partial parsing
- Outputs: `CHANNEL_NAME_full.md` files

## Output Location

Save extracted content to:
```
D:/Documents/cmw-rag-channel-extractions/CHANNEL_NAME.md
```

## Workflow Summary

```
Public channel?
  → Method 1: Playwright preview, extract text via DOM
  
Private/closed channel?
  → Method 2: Playwright headed, user logs in, session persists
  → Use OCR only for clicking/typing in browser
  → Extract text via DOM selectors
  
Have Desktop export?
  → Method 3: Run extract_all_chats.py
```

## See Also

- [Telethon Docs](https://docs.telethon.dev/) - API alternative
- [Playwright Skill](../playwright-cli/SKILL.md) - Browser automation
- [Telegram Desktop](https://desktop.telegram.org/) - Export tool