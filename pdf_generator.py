#!/usr/bin/env python3
"""
PDF Generator for Bramble LP Pitch Tool
Converts pitch content to a styled PDF using fpdf2 (pure Python, works on Streamlit Cloud).
"""

import io
import re
from datetime import datetime
from fpdf import FPDF


# Bramble brand colors (RGB)
BRAMBLE_GREEN = (45, 80, 22)  # #2d5016
GOLD_ACCENT = (201, 162, 39)  # #c9a227
CREAM_BG = (248, 246, 240)    # #f8f6f0
DARK_TEXT = (51, 51, 51)      # #333333


class BramblePDF(FPDF):
    """Custom PDF class with Bramble branding."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        pass  # No header

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(102, 102, 102)
        self.cell(0, 10, f'Page {self.page_no()}', align='R')

    def add_title(self, text):
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(*BRAMBLE_GREEN)
        self.cell(0, 12, text, ln=True)
        # Gold underline
        self.set_draw_color(*GOLD_ACCENT)
        self.set_line_width(1)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def add_subtitle(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(102, 102, 102)
        self.multi_cell(0, 5, text)
        self.ln(8)

    def add_section_header(self, text):
        self.ln(5)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(*BRAMBLE_GREEN)
        self.cell(0, 8, text, ln=True)
        # Light underline
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def add_highlight_box(self, text, box_type='default'):
        """Add a highlighted box with content."""
        self.ln(2)
        x = self.get_x()
        y = self.get_y()

        # Set colors based on box type
        if box_type == 'hook':
            bg_color = (232, 244, 232)  # Light green
            border_color = BRAMBLE_GREEN
        elif box_type == 'warning':
            bg_color = (255, 248, 230)  # Light yellow
            border_color = GOLD_ACCENT
        else:
            bg_color = CREAM_BG
            border_color = GOLD_ACCENT

        # Calculate height needed
        self.set_font('Helvetica', '', 11)
        # Estimate lines needed
        text_width = 175
        lines = len(text) / 80 + text.count('\n') + 1
        box_height = max(lines * 6 + 10, 20)

        # Draw background
        self.set_fill_color(*bg_color)
        self.rect(x, y, 190, box_height, 'F')

        # Draw left border
        self.set_draw_color(*border_color)
        self.set_line_width(1.2)
        self.line(x, y, x, y + box_height)

        # Add text
        self.set_xy(x + 5, y + 4)
        self.set_text_color(*DARK_TEXT)
        self._add_formatted_text(text, text_width)

        self.set_y(y + box_height + 4)

    def add_body_text(self, text):
        """Add body text with markdown-style bold support."""
        self.set_font('Helvetica', '', 11)
        self.set_text_color(*DARK_TEXT)
        self._add_formatted_text(text, 185)
        self.ln(3)

    def _add_formatted_text(self, text, width):
        """Add text with **bold** markdown support."""
        if not text:
            return

        # Split into paragraphs
        paragraphs = text.split('\n\n')

        for i, para in enumerate(paragraphs):
            if not para.strip():
                continue

            # Handle single newlines as line breaks
            lines = para.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Parse **bold** markers
                parts = re.split(r'(\*\*[^*]+\*\*)', line)

                x_start = self.get_x()
                current_x = x_start

                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        # Bold text
                        bold_text = part[2:-2]
                        self.set_font('Helvetica', 'B', 11)
                        self.set_text_color(*BRAMBLE_GREEN)
                        part_width = self.get_string_width(bold_text)

                        if current_x + part_width > x_start + width:
                            self.ln(5)
                            current_x = x_start

                        self.set_x(current_x)
                        self.cell(part_width, 5, bold_text)
                        current_x += part_width
                    elif part:
                        # Regular text
                        self.set_font('Helvetica', '', 11)
                        self.set_text_color(*DARK_TEXT)

                        words = part.split(' ')
                        for word in words:
                            if not word:
                                continue
                            word_width = self.get_string_width(word + ' ')
                            if current_x + word_width > x_start + width:
                                self.ln(5)
                                current_x = x_start
                            self.set_x(current_x)
                            self.cell(word_width, 5, word + ' ')
                            current_x += word_width

                self.ln(5)

            if i < len(paragraphs) - 1:
                self.ln(3)


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
    pdf = BramblePDF()
    pdf.add_page()

    # Title
    pdf.add_title("Bramble Investments")
    pdf.add_subtitle(f"Personalised Pitch for {lp_name}\nGenerated: {datetime.now().strftime('%d %B %Y')}")

    # LP Profile
    pdf.add_section_header("LP Profile")
    pdf.add_highlight_box(pitch.get('lp_summary', 'N/A'))

    # Opening Hook
    pdf.add_section_header("Opening Hook")
    pdf.add_highlight_box(pitch.get('opening_hook', 'N/A'), box_type='hook')

    # Thesis Framing
    pdf.add_section_header("Investment Thesis Framing")
    pdf.add_body_text(pitch.get('thesis_framing', 'N/A'))

    # Tailwinds
    pdf.add_section_header("Market Tailwinds to Emphasise")
    pdf.add_body_text(pitch.get('tailwinds_emphasis', 'N/A'))

    # Team
    pdf.add_section_header("Team & Advisors to Feature")
    pdf.add_body_text(pitch.get('team_highlights', 'N/A'))

    # Value-Add
    pdf.add_section_header("Value-Add Framing")
    pdf.add_body_text(pitch.get('value_add_framing', 'N/A'))

    # Questions
    pdf.add_section_header("Anticipated Questions")
    pdf.add_body_text(pitch.get('anticipated_questions', 'N/A'))

    # Conversation Starters
    pdf.add_section_header("Conversation Starters")
    pdf.add_body_text(pitch.get('conversation_starters', 'N/A'))

    # Concerns
    pdf.add_section_header("Potential Concerns to Address")
    pdf.add_highlight_box(pitch.get('risks_to_address', 'N/A'), box_type='warning')

    # Footer
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(102, 102, 102)
    pdf.cell(0, 10, "Prepared by Bramble LP Pitch Tool | Confidential", align='C')

    # Output
    return bytes(pdf.output())


if __name__ == "__main__":
    # Test
    test_pitch = {
        "lp_summary": "Test LP is a family office focused on sustainable investments.",
        "opening_hook": "Bramble's thesis aligns perfectly with your focus.",
        "thesis_framing": "We emphasise **Sustainable Production** given your portfolio.",
        "tailwinds_emphasis": "**GLP-1:** Relevant because of health focus...\n\n**AI:** Also relevant for supply chain...",
        "team_highlights": "**Henry Dimbleby:** Key for policy connections...",
        "value_add_framing": "Our advisory practice provides unique insights.",
        "anticipated_questions": "**Q: Why food?**\nA: Because food systems need transformation...",
        "conversation_starters": "1. Ask about their recent investment in health tech...",
        "risks_to_address": "**Fund Size:** They may worry about fund size. Address by emphasising focused portfolio."
    }

    pdf = generate_pdf("Test LP", test_pitch, {})
    with open("test_pitch.pdf", "wb") as f:
        f.write(pdf)
    print("Test PDF generated: test_pitch.pdf")
