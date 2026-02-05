#!/usr/bin/env python3
"""
PDF Generator for Bramble LP Pitch Tool
Converts pitch content to a styled PDF using weasyprint.
"""

import io
from datetime import datetime

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

try:
    import markdown2
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


# Bramble-styled CSS
PDF_CSS = """
@page {
    size: A4;
    margin: 2cm 2.5cm;
    @bottom-right {
        content: counter(page);
        font-size: 10px;
        color: #666;
    }
}

body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #333;
}

h1 {
    color: #2d5016;
    font-size: 24pt;
    font-weight: 600;
    border-bottom: 3px solid #c9a227;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

h2 {
    color: #2d5016;
    font-size: 14pt;
    font-weight: 600;
    margin-top: 25px;
    margin-bottom: 10px;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
}

h3 {
    color: #555;
    font-size: 12pt;
    font-weight: 600;
    margin-top: 15px;
    margin-bottom: 8px;
}

.subtitle {
    color: #666;
    font-size: 10pt;
    margin-bottom: 30px;
}

.summary-box {
    background-color: #f8f6f0;
    border-left: 4px solid #c9a227;
    padding: 15px;
    margin: 15px 0;
}

.hook-box {
    background-color: #e8f4e8;
    border: 1px solid #2d5016;
    border-radius: 5px;
    padding: 15px;
    margin: 15px 0;
    font-style: italic;
}

.warning-box {
    background-color: #fff8e6;
    border-left: 4px solid #c9a227;
    padding: 15px;
    margin: 15px 0;
}

p {
    margin-bottom: 10px;
}

strong {
    color: #2d5016;
}

.section {
    margin-bottom: 20px;
    page-break-inside: avoid;
}

.footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
    font-size: 9pt;
    color: #666;
}
"""


def generate_pdf(lp_name: str, pitch: dict, research: dict) -> bytes:
    """
    Generate a styled PDF from pitch content.

    Args:
        lp_name: Name of the LP
        pitch: Dict containing personalised pitch sections
        research: Dict containing research data

    Returns:
        PDF as bytes
    """
    if not WEASYPRINT_AVAILABLE:
        raise ImportError("weasyprint is required for PDF generation")

    # Build HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Bramble Pitch - {lp_name}</title>
    </head>
    <body>
        <h1>Bramble Investments</h1>
        <p class="subtitle">Personalised Pitch for <strong>{lp_name}</strong><br>
        Generated: {datetime.now().strftime('%d %B %Y')}</p>

        <div class="section">
            <h2>LP Profile</h2>
            <div class="summary-box">
                {_escape_html(pitch.get('lp_summary', 'N/A'))}
            </div>
        </div>

        <div class="section">
            <h2>Opening Hook</h2>
            <div class="hook-box">
                {_escape_html(pitch.get('opening_hook', 'N/A'))}
            </div>
        </div>

        <div class="section">
            <h2>Investment Thesis Framing</h2>
            {_format_content(pitch.get('thesis_framing', 'N/A'))}
        </div>

        <div class="section">
            <h2>Market Tailwinds to Emphasise</h2>
            {_format_content(pitch.get('tailwinds_emphasis', 'N/A'))}
        </div>

        <div class="section">
            <h2>Team & Advisors to Feature</h2>
            {_format_content(pitch.get('team_highlights', 'N/A'))}
        </div>

        <div class="section">
            <h2>Value-Add Framing</h2>
            {_format_content(pitch.get('value_add_framing', 'N/A'))}
        </div>

        <div class="section">
            <h2>Anticipated Questions</h2>
            {_format_content(pitch.get('anticipated_questions', 'N/A'))}
        </div>

        <div class="section">
            <h2>Conversation Starters</h2>
            {_format_content(pitch.get('conversation_starters', 'N/A'))}
        </div>

        <div class="section">
            <h2>Potential Concerns to Address</h2>
            <div class="warning-box">
                {_format_content(pitch.get('risks_to_address', 'N/A'))}
            </div>
        </div>

        <div class="footer">
            <p>Prepared by Bramble LP Pitch Tool | Confidential</p>
        </div>
    </body>
    </html>
    """

    # Generate PDF
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(
        pdf_buffer,
        stylesheets=[CSS(string=PDF_CSS)]
    )
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not isinstance(text, str):
        text = str(text)
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))


def _format_content(text: str) -> str:
    """Format content for HTML display, handling markdown-like formatting."""
    if not isinstance(text, str):
        # Handle case where it's still a list/array
        if isinstance(text, list):
            text = "\n\n".join(str(item) for item in text)
        else:
            text = str(text)

    # Escape HTML first
    text = _escape_html(text)

    # Convert **bold** to <strong>
    import re
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)

    # Convert newlines to proper HTML
    paragraphs = text.split('\n\n')
    formatted = []
    for p in paragraphs:
        p = p.strip()
        if p:
            # Handle single newlines within paragraphs
            p = p.replace('\n', '<br>')
            formatted.append(f'<p>{p}</p>')

    return '\n'.join(formatted)


if __name__ == "__main__":
    # Test
    test_pitch = {
        "lp_summary": "Test LP is a family office focused on sustainable investments.",
        "opening_hook": "Bramble's thesis aligns perfectly with your focus.",
        "thesis_framing": "We emphasise **Sustainable Production** given your portfolio.",
        "tailwinds_emphasis": "**GLP-1**: Relevant because...\n\n**AI**: Also relevant...",
        "portfolio_highlights": "**Klura Labs**: Great fit because...",
        "team_highlights": "**Henry Dimbleby**: Key for policy...",
        "value_add_framing": "Our advisory practice provides...",
        "anticipated_questions": "**Q: Why food?**\nA: Because...",
        "conversation_starters": "1. Ask about their recent investment...",
        "risks_to_address": "They may worry about fund size."
    }

    pdf = generate_pdf("Test LP", test_pitch, {})
    with open("test_pitch.pdf", "wb") as f:
        f.write(pdf)
    print("Test PDF generated: test_pitch.pdf")
