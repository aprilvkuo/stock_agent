---
name: resend-email-sender
description: Send emails using Resend API with beautiful HTML templates. Support 4 themes (finance/simple/dark/minimal), auto Markdown conversion, section title detection, and responsive design. Use when the user needs to send professional-looking emails without SMTP configuration.
---

# Resend Email Sender

Send emails via Resend API with beautiful HTML themes.

## Quick Start

### 1. Configure

Set environment variables in `.env`:

```bash
RESEND_API_KEY=your_resend_api_key
RESEND_FROM=onboarding@resend.dev  # Optional
RESEND_TO=your-email@example.com    # Optional default recipient
```

Get API key at https://resend.com

### 2. Send Email

```bash
openclaw run resend-email-sender \
  --to="recipient@example.com" \
  --subject="Hello" \
  --text="Plain text message"
```

## Usage

### Basic Text Email with Auto HTML

```bash
openclaw run resend-email-sender \
  --to="user@example.com" \
  --subject="Notification" \
  --text="## Task Complete\n\nYour task is **finished**!\n\nCheck [details](https://example.com)"
```

### Theme Options

Choose from 4 beautiful themes:

| Theme | Description |
|-------|-------------|
| `simple` | Clean and minimal (default) |
| `finance` | Professional finance report style |
| `dark` | Eye-friendly dark mode |
| `minimal` | Ultra-simple plain style |

```bash
# Finance theme (great for reports)
openclaw run resend-email-sender \
  --to="user@example.com" \
  --subject="Daily Report" \
  --text="【今日概览】\n\n市场分析..." \
  --theme="finance"

# Dark theme (great for night reading)
openclaw run resend-email-sender \
  --to="user@example.com" \
  --subject="Evening Update" \
  --text="# Evening Update\n\n..." \
  --theme="dark"
```

### Auto Markdown Features

The script automatically converts these Markdown formats:

| Format | Result |
|--------|--------|
| `**bold**` | Bold text |
| `*italic*` | Italic text |
| `[text](url)` | Links |
| `# Heading` | Section titles |
| `## Heading` | Section titles |
| `【Section】` | Section titles |
| `[Section]` | Section titles |

### Multiple Recipients

```bash
openclaw run resend-email-sender \
  --to="user1@example.com,user2@example.com" \
  --subject="Team Update" \
  --text="Meeting at 3 PM."
```

### CC and BCC

```bash
openclaw run resend-email-sender \
  --to="primary@example.com" \
  --cc="manager@example.com" \
  --bcc="archive@example.com" \
  --subject="Report" \
  --text="Please find the report."
```

### Custom HTML

```bash
openclaw run resend-email-sender \
  --to="user@example.com" \
  --subject="Welcome" \
  --html="<h1>Welcome!</h1><p>Thanks for joining.</p>"
```

### Disable Auto HTML

```bash
openclaw run resend-email-sender \
  --to="user@example.com" \
  --subject="Plain Text" \
  --text="Just plain text, no HTML" \
  --no-auto-html
```

## Configuration Options

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RESEND_API_KEY` | Yes | - | Your Resend API key |
| `RESEND_FROM` | No | `onboarding@resend.dev` | Default sender address |
| `RESEND_TO` | No | - | Default recipient address |

## Resources

- `scripts/send_email.py` - Main email sending script with theme support
