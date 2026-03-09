#!/usr/bin/env python3
"""
Resend Email Sender - Enhanced with beautiful HTML templates

Send emails via Resend API with auto HTML conversion and beautiful themes.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RESEND_API_URL = "https://api.resend.com/emails"


def get_html_theme(theme):
    """Get CSS theme for email."""
    themes = {
        'finance': """
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; margin: 0; }
            .container { max-width: 900px; margin: 0 auto; background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }
            .header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 30px; text-align: center; }
            .header h1 { font-size: 32px; margin-bottom: 8px; font-weight: 700; margin-top: 0; }
            .header p { font-size: 14px; opacity: 0.9; margin: 0; }
            .content { padding: 30px; }
            .section { margin-bottom: 24px; }
            .section-title { font-size: 22px; font-weight: 700; color: #1e3c72; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 3px solid #667eea; display: flex; align-items: center; }
            .text-content { line-height: 1.8; color: #333; font-size: 15px; }
            .text-content p { margin-bottom: 12px; }
            .footer { background: #1e3c72; color: white; padding: 24px; text-align: center; }
            .footer p { margin-bottom: 8px; font-size: 14px; }
        """,
        'simple': """
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif; background: #f5f5f5; min-height: 100vh; padding: 20px; margin: 0; }
            .container { max-width: 700px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }
            .header { background: #4a5568; color: white; padding: 24px; text-align: center; }
            .header h1 { font-size: 24px; margin-bottom: 4px; font-weight: 600; margin-top: 0; }
            .content { padding: 24px; }
            .text-content { line-height: 1.7; color: #333; font-size: 15px; }
            .footer { background: #4a5568; color: white; padding: 16px; text-align: center; font-size: 13px; }
        """,
        'dark': """
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif; background: #1a202c; min-height: 100vh; padding: 20px; margin: 0; }
            .container { max-width: 900px; margin: 0 auto; background: #2d3748; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); overflow: hidden; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
            .header h1 { font-size: 32px; margin-bottom: 8px; font-weight: 700; margin-top: 0; }
            .content { padding: 30px; }
            .text-content { line-height: 1.8; color: #e2e8f0; font-size: 15px; }
            .footer { background: #667eea; color: white; padding: 24px; text-align: center; }
        """,
        'minimal': """
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif; background: white; padding: 20px; margin: 0; }
            .container { max-width: 600px; margin: 0 auto; }
            .header { color: #333; padding: 20px 0; border-bottom: 1px solid #eee; }
            .header h1 { font-size: 20px; font-weight: 600; margin: 0; }
            .content { padding: 20px 0; }
            .text-content { line-height: 1.6; color: #333; font-size: 15px; }
            .footer { color: #999; padding: 20px 0; border-top: 1px solid #eee; font-size: 13px; }
        """
    }
    return themes.get(theme, themes['simple'])


def auto_convert_text_to_html(text, theme='simple', title=None):
    """Convert plain text to beautiful HTML with theme support."""
    if not text:
        return None
    
    lines = text.strip().split('\n')
    email_title = title or lines[0] if lines else 'Email'
    
    css = get_html_theme(theme)
    
    # Process text content
    html_lines = []
    in_paragraph = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            continue
        
        # Section title detection
        is_section = (
            (stripped.startswith('[') and stripped.endswith(']')) or
            (stripped.startswith('【') and stripped.endswith('】')) or
            (stripped.startswith('==') and stripped.endswith('==')) or
            (stripped.startswith('--') and stripped.endswith('--')) or
            stripped.startswith('# ') or
            stripped.startswith('## ') or
            stripped.startswith('### ')
        )
        
        if is_section:
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            
            section_title = stripped.replace('[', '').replace(']', '').replace('【', '').replace('】', '')
            section_title = section_title.replace('=', '').replace('-', '').replace('#', '').strip()
            html_lines.append(f'<div class="section-title">{section_title}</div>')
            html_lines.append('<div class="text-content"><p>')
            in_paragraph = True
            continue
        
        # Regular text with formatting
        if not in_paragraph:
            html_lines.append('<div class="text-content"><p>')
            in_paragraph = True
        
        # Escape HTML
        formatted_line = stripped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Markdown formatting
        formatted_line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', formatted_line)
        formatted_line = re.sub(r'__(.+?)__', r'<b>\1</b>', formatted_line)
        formatted_line = re.sub(r'\*(.+?)\*', r'<i>\1</i>', formatted_line)
        formatted_line = re.sub(r'_(.+?)_', r'<i>\1</i>', formatted_line)
        formatted_line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', formatted_line)
        
        html_lines.append(formatted_line)
    
    # Close any open paragraph
    if in_paragraph:
        html_lines.append('</p>')
    
    html_content = '\n'.join(html_lines)
    
    # Build full HTML
    html = f'''<!DOCTYPE html>
<html>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>{email_title}</title>
  <style>{css}</style>
</head>
<body>
  <div class='container'>
    <div class='header'>
      <h1>{email_title}</h1>
    </div>
    <div class='content'>
      <div class='section'>
        {html_content}
      </div>
    </div>
    <div class='footer'>
      <p>Sent via Resend Email Sender Skill</p>
    </div>
  </div>
</body>
</html>'''
    
    return html


def load_env():
    """Load environment from .env files."""
    paths = [
        Path.home() / '.openclaw' / 'workspace' / '.env',
        Path('.env').resolve(),
    ]
    for path in paths:
        if path.exists():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip('"\'')
                        if k not in os.environ:
                            os.environ[k] = v
            break


def get_config():
    """Get Resend configuration."""
    api_key = os.getenv('RESEND_API_KEY', '')
    from_email = os.getenv('RESEND_FROM', 'onboarding@resend.dev')
    default_to = os.getenv('RESEND_TO', '')
    
    if not api_key:
        print("Error: RESEND_API_KEY not configured")
        print("\nSet in .env file:")
        print("  RESEND_API_KEY=your_api_key")
        print("\nGet API key: https://resend.com")
        sys.exit(1)
    
    return {
        'api_key': api_key,
        'from': from_email,
        'default_to': default_to,
    }


def send_email(config, to, subject, text=None, html=None, cc=None, bcc=None, 
               auto_html=True, theme='simple'):
    """Send email via Resend API."""
    
    payload = {
        'from': config['from'],
        'to': to if isinstance(to, list) else [to],
        'subject': subject,
    }
    
    if text:
        payload['text'] = text
        # Auto-convert text to HTML if not provided
        if auto_html and not html:
            html = auto_convert_text_to_html(text, theme=theme, title=subject)
    
    if html:
        payload['html'] = html
    if cc:
        payload['cc'] = cc if isinstance(cc, list) else cc.split(',')
    if bcc:
        payload['bcc'] = bcc if isinstance(bcc, list) else bcc.split(',')
    
    try:
        curl_cmd = [
            'curl', '-s', '-X', 'POST',
            RESEND_API_URL,
            '-H', f'Authorization: Bearer {config["api_key"]}',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps(payload)
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                if 'id' in response:
                    return True, f"Email sent! ID: {response['id']}"
                else:
                    return False, f"Unexpected response: {result.stdout}"
            except json.JSONDecodeError:
                return False, f"Invalid response: {result.stdout}"
        else:
            error = result.stderr or result.stdout or "Unknown error"
            return False, f"Failed: {error}"
    
    except Exception as e:
        return False, f"Failed: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description='Send email via Resend API with beautiful HTML themes')
    parser.add_argument('--to', help='Recipients (comma-separated, uses RESEND_TO by default)')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--text', help='Plain text content (auto-converts to HTML)')
    parser.add_argument('--html', help='HTML content (overrides auto-conversion)')
    parser.add_argument('--theme', default='simple', 
                        help='HTML theme: finance/simple/dark/minimal (default: simple)')
    parser.add_argument('--no-auto-html', action='store_true', help='Disable auto HTML conversion from text')
    parser.add_argument('--cc', help='CC recipients (comma-separated)')
    parser.add_argument('--bcc', help='BCC recipients (comma-separated)')
    
    args = parser.parse_args()
    
    if not args.text and not args.html:
        print("Error: Provide --text or --html")
        sys.exit(1)
    
    load_env()
    config = get_config()
    
    # Determine recipients
    if args.to:
        to_list = args.to.split(',')
    elif config['default_to']:
        to_list = config['default_to'].split(',')
    else:
        print("Error: --to is required or set RESEND_TO in .env")
        sys.exit(1)
    
    cc_list = args.cc.split(',') if args.cc else None
    bcc_list = args.bcc.split(',') if args.bcc else None
    
    success, message = send_email(
        config=config,
        to=to_list,
        subject=args.subject,
        text=args.text,
        html=args.html,
        cc=cc_list,
        bcc=bcc_list,
        auto_html=not args.no_auto_html,
        theme=args.theme
    )
    
    print(message)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
