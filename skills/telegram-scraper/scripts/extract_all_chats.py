#!/usr/bin/env python3
"""Extract all text content from Telegram chat exports.

This script extracts text messages from result.json files in Telegram chat export folders.
It handles corrupted JSON by using partial parsing and extracts:
- Message text content
- Message types (text, photo, video, link, etc.)
- Sender information
- Timestamps
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Any


def extract_json_objects(text: str) -> list[dict]:
    """Extract JSON objects from potentially corrupted JSON text."""
    objects = []
    depth = 0
    start = None
    in_string = False
    escape_next = False
    
    for i, char in enumerate(text):
        if escape_next:
            escape_next = False
            continue
        if char == '\\' and in_string:
            escape_next = True
            continue
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == '{':
            if depth == 0:
                start = i
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    obj = json.loads(text[start:i+1])
                    objects.append(obj)
                except json.JSONDecodeError:
                    pass
                start = None
    return objects


def parse_message(msg: dict) -> dict | None:
    """Parse a single message and extract relevant content."""
    result = {
        'id': msg.get('id'),
        'type': msg.get('type', 'unknown'),
        'date': msg.get('date'),
        'from': msg.get('from'),
        'from_id': msg.get('from_id'),
        'text': '',
        'text_entities': [],
        'media_type': None,
        'links': [],
        'forwarded_from': None,
        'reply_to': None,
    }
    
    # Extract text content
    text_content = msg.get('text', '')
    if isinstance(text_content, str):
        result['text'] = text_content
    elif isinstance(text_content, list):
        # Text can be a list of text entities
        text_parts = []
        for entity in text_content:
            if isinstance(entity, str):
                text_parts.append(entity)
            elif isinstance(entity, dict):
                text_parts.append(entity.get('text', ''))
        result['text'] = ''.join(text_parts)
        result['text_entities'] = [
            e for e in text_content 
            if isinstance(e, dict) and e.get('type') == 'link'
        ]
    
    # Extract links from text entities
    for entity in result['text_entities']:
        if isinstance(entity, dict) and entity.get('type') == 'link':
            result['links'].append(entity.get('text', ''))
    
    # Media type
    if 'photo' in msg:
        result['media_type'] = 'photo'
    elif 'video' in msg:
        result['media_type'] = 'video'
    elif 'file' in msg:
        result['media_type'] = 'file'
    elif 'media_type' in msg:
        result['media_type'] = msg['media_type']
    
    # Forward info
    if 'forwarded_from' in msg:
        result['forwarded_from'] = msg['forwarded_from']
    
    # Reply info
    if 'reply_to_message_id' in msg:
        result['reply_to'] = msg['reply_to_message_id']
    
    return result


def extract_channel_content(json_path: Path) -> dict:
    """Extract all content from a channel export."""
    print(f"\nProcessing: {json_path.parent.name}")
    
    with open(json_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Try direct JSON parse first
    try:
        data = json.loads(content)
        channel_name = data.get('name', json_path.parent.name)
        messages = data.get('messages', [])
        print(f"  Channel: {channel_name}")
        print(f"  Messages: {len(messages)}")
    except json.JSONDecodeError as e:
        print(f"  JSON error: {e}")
        print(f"  Attempting partial extraction...")
        
        # Extract channel name
        name_match = re.search(r'"name":\s*"([^"]+)"', content)
        channel_name = name_match.group(1) if name_match else json_path.parent.name
        
        # Extract messages as individual JSON objects
        messages = extract_json_objects(content)
        
        # Filter to only message objects (those with 'id' and 'type' fields)
        messages = [m for m in messages if 'id' in m and 'type' in m]
        
        print(f"  Channel: {channel_name}")
        print(f"  Extracted messages: {len(messages)}")
    
    # Parse all messages
    parsed_messages = []
    for msg in messages:
        parsed = parse_message(msg)
        if parsed and parsed['text']:
            parsed_messages.append(parsed)
    
    return {
        'channel_name': channel_name,
        'message_count': len(messages),
        'text_messages': parsed_messages,
        'export_path': str(json_path.parent),
    }


def format_messages_for_markdown(data: dict, max_messages: int = None) -> str:
    """Format extracted messages as markdown."""
    lines = []
    lines.append(f"# {data['channel_name']}\n")
    lines.append(f"**Export:** {Path(data['export_path']).name}")
    lines.append(f"**Messages:** {data['message_count']} ({len(data['text_messages'])} with text)\n")
    lines.append("---\n")
    
    messages = data['text_messages']
    if max_messages:
        messages = messages[:max_messages]
    
    current_date = None
    for msg in messages:
        # Group by date
        msg_date = msg.get('date', '')[:10] if msg.get('date') else None
        if msg_date!= current_date:
            if current_date is not None:
                lines.append("")
            lines.append(f"## {msg_date}\n")
            current_date = msg_date
        
        sender = msg.get('from', 'Unknown')
        text = msg.get('text', '').strip()
        
        if not text:
            continue
        
        # Add media type indicator
        media = msg.get('media_type')
        if media:
            text = f"[{media}] {text}"
        
        # Add forwarded indicator
        if msg.get('forwarded_from'):
            text = f"↩️ forwarded from {msg['forwarded_from']}\n\n{text}"
        
        lines.append(f"**{sender}:**\n{text}\n")
    
    return '\n'.join(lines)


def main():
    """Main extraction function."""
    base_dirs = [
        Path("D:/Documents/cmw-rag-channel-extractions"),
        Path("E:/Downloads/Telegram Desktop"),
    ]
    
    all_channels = []
    
    for base_dir in base_dirs:
        if not base_dir.exists():
            print(f"Directory not found: {base_dir}")
            continue
        
        # Find all ChatExport folders
        export_dirs = sorted(base_dir.glob("ChatExport_*"))
        
        for export_dir in export_dirs:
            json_path = export_dir / "result.json"
            if json_path.exists():
                try:
                    data = extract_channel_content(json_path)
                    all_channels.append(data)
                except Exception as e:
                    print(f"Error processing {export_dir}: {e}")
    
    # Save each channel as separate markdown file
    output_dir = Path("D:/Documents/cmw-rag-channel-extractions")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for channel_data in all_channels:
        # Clean channel name for filename
        safe_name = re.sub(r'[^\w\s-]', '', channel_data['channel_name'])
        safe_name = re.sub(r'[-\s]+', '_', safe_name).strip('_').lower()
        if not safe_name:
            safe_name = f"channel_{all_channels.index(channel_data)}"
        
        output_path = output_dir / f"{safe_name}_full.md"
        markdown = format_messages_for_markdown(channel_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"  Saved: {output_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    total_messages = sum(c['message_count'] for c in all_channels)
    total_text = sum(len(c['text_messages']) for c in all_channels)
    print(f"Channels: {len(all_channels)}")
    print(f"Total messages: {total_messages}")
    print(f"Messages with text: {total_text}")
    
    return all_channels


if __name__ == "__main__":
    main()