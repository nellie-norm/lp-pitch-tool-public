#!/usr/bin/env python3
"""
Bramble LP Pitch Personalization Tool

Takes an LP name, researches them via Perplexity, and generates
personalized pitch text tailored to their investment focus and interests.
"""

import os
import sys
import json
import argparse
from datetime import datetime
import anthropic
import requests

# =============================================================================
# CONFIGURATION
# =============================================================================

# Placeholder pitch content - actual content loaded from secrets
BRAMBLE_PITCH_PLACEHOLDER = """
YOUR FUND NAME - CORE PITCH CONTENT

Add your fund's pitch content to .streamlit/secrets.toml under the key BRAMBLE_PITCH.

Include sections for:
- Fund Overview (size, stage, check size, geography, etc.)
- Investment Thesis
- Market Tailwinds
- Portfolio Companies
- Team
- Value-Add
"""

def get_bramble_pitch():
    """Load Bramble pitch content from secrets or environment."""
    # Try Streamlit secrets first
    try:
        import streamlit as st
        if "BRAMBLE_PITCH" in st.secrets:
            return st.secrets["BRAMBLE_PITCH"]
    except:
        pass

    # Try environment variable
    if os.environ.get("BRAMBLE_PITCH"):
        return os.environ.get("BRAMBLE_PITCH")

    # Try local secrets file
    secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        with open(secrets_path, "rb") as f:
            secrets = tomllib.load(f)
            if "BRAMBLE_PITCH" in secrets:
                return secrets["BRAMBLE_PITCH"]

    return BRAMBLE_PITCH_PLACEHOLDER

# Load pitch content
BRAMBLE_PITCH = get_bramble_pitch()

# =============================================================================
# API HELPERS
# =============================================================================

def get_perplexity_key():
    """Get Perplexity API key from various sources."""
    # Check Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        if "PERPLEXITY_API_KEY" in st.secrets:
            return st.secrets["PERPLEXITY_API_KEY"]
    except:
        pass

    # Check environment
    if os.environ.get("PERPLEXITY_API_KEY"):
        return os.environ.get("PERPLEXITY_API_KEY")

    # Check .secrets.toml in parent project
    secrets_path = os.path.expanduser("~/vc_screen_public/.secrets.toml")
    if os.path.exists(secrets_path):
        with open(secrets_path, "r") as f:
            for line in f:
                if "PERPLEXITY_API_KEY" in line:
                    return line.split("=")[1].strip().strip('"')

    # Check standalone file
    key_path = os.path.expanduser("~/.perplexity_key")
    if os.path.exists(key_path):
        with open(key_path, "r") as f:
            return f.read().strip()

    return None


def get_anthropic_key():
    """Get Anthropic API key from various sources."""
    # Check Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except:
        pass

    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ.get("ANTHROPIC_API_KEY")

    secrets_path = os.path.expanduser("~/vc_screen_public/.secrets.toml")
    if os.path.exists(secrets_path):
        with open(secrets_path, "r") as f:
            for line in f:
                if "ANTHROPIC_API_KEY" in line:
                    return line.split("=")[1].strip().strip('"')

    key_path = os.path.expanduser("~/.api_key")
    if os.path.exists(key_path):
        with open(key_path, "r") as f:
            return f.read().strip()

    return None


# =============================================================================
# RESEARCH FUNCTIONS
# =============================================================================

def _perplexity_query(query: str, api_key: str) -> dict:
    """Make a single Perplexity API call."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 2500,
        "temperature": 0.1
    }
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    result = response.json()
    text = result["choices"][0]["message"]["content"]
    citations = result.get("citations", [])
    return {"text": text, "citations": citations}


def research_lp(lp_name: str, additional_context: str = "") -> dict:
    """
    Research a potential LP using multiple focused Perplexity queries:
    1. Organisation overview and decision makers
    2. Investment history and portfolio
    3. Recent news and strategic priorities
    """
    api_key = get_perplexity_key()
    if not api_key:
        return {"error": "No Perplexity API key found", "research": ""}

    context_note = f" Context: {additional_context}" if additional_context else ""
    all_citations = []
    research_sections = []

    # Query 1: Organisation Overview
    query1 = f"""Research "{lp_name}" as a potential investor/LP.{context_note}

Focus ONLY on organisation overview:
- What type of investor are they? (family office, pension fund, corporate, endowment, fund of funds, sovereign wealth, HNWI, etc.)
- AUM and investment capacity
- Geographic focus and headquarters
- Key decision makers and their backgrounds (names, roles, career history)
- Organisational structure and governance

Be specific with facts, names, and figures. Cite sources."""

    # Query 2: Investment Focus & History
    query2 = f"""Research "{lp_name}" investment history and focus.{context_note}

Focus ONLY on their investments:
- What sectors/themes do they invest in?
- What stages do they back (seed, Series A, growth, funds)?
- Notable investments (especially food, sustainability, health, agtech, climate)
- Stated investment thesis or mandate
- ESG/impact requirements or frameworks
- What they look for in fund managers

Be specific with deal names, amounts, dates. Cite sources."""

    # Query 3: Recent News & Strategic Priorities
    query3 = f"""Research "{lp_name}" recent news and strategic priorities.{context_note}

Focus ONLY on recent activity (last 2 years):
- Recent investments or fund commitments
- Strategy announcements or pivots
- Leadership changes
- Key partnerships or relationships
- Public statements about priorities
- Any controversies or concerns

Be specific with dates and details. Cite sources."""

    try:
        # Run queries sequentially (could parallelise but keeps it simple)
        print("  - Researching organisation overview...", file=sys.stderr)
        r1 = _perplexity_query(query1, api_key)
        research_sections.append(f"## Organisation Overview\n\n{r1['text']}")
        all_citations.extend(r1.get("citations", []))

        print("  - Researching investment history...", file=sys.stderr)
        r2 = _perplexity_query(query2, api_key)
        research_sections.append(f"## Investment Focus & History\n\n{r2['text']}")
        all_citations.extend(r2.get("citations", []))

        print("  - Researching recent news...", file=sys.stderr)
        r3 = _perplexity_query(query3, api_key)
        research_sections.append(f"## Recent News & Priorities\n\n{r3['text']}")
        all_citations.extend(r3.get("citations", []))

        # Combine research
        research_text = "\n\n".join(research_sections)

        # Deduplicate citations
        unique_citations = list(dict.fromkeys(all_citations))
        if unique_citations:
            research_text += "\n\n## Sources\n" + "\n".join(f"- {c}" for c in unique_citations)

        return {
            "lp_name": lp_name,
            "research": research_text,
            "citations": unique_citations
        }

    except Exception as e:
        return {"error": str(e), "research": "", "lp_name": lp_name}


# =============================================================================
# PITCH PERSONALIZATION
# =============================================================================

def generate_personalized_pitch(lp_name: str, research: str, additional_notes: str = "") -> dict:
    """
    Generate personalized pitch text for each section based on LP research.

    Returns a dict with personalized text for each major section.
    """
    api_key = get_anthropic_key()
    if not api_key:
        return {"error": "No Anthropic API key found"}

    client = anthropic.Anthropic(api_key=api_key)

    notes_section = f"\n\nADDITIONAL NOTES FROM THE TEAM:\n{additional_notes}" if additional_notes else ""

    prompt = f"""You are helping Bramble Investments prepare for an LP meeting with {lp_name}.

Based on the research below, generate PERSONALISED pitch content that makes Bramble's proposition maximally relevant to this specific LP. Keep Bramble's core identity but frame everything through the lens of what matters to {lp_name}.

=== RESEARCH ON {lp_name.upper()} ===
{research}
{notes_section}

=== BRAMBLE'S CORE PITCH ===
{BRAMBLE_PITCH}

=== YOUR TASK ===

Generate personalised text for each section below. For each section:
- Keep Bramble's facts accurate
- Frame and emphasise what resonates with this LP
- Add specific "hooks" connecting Bramble to LP interests
- Use British English
- Be specific, not generic

Output as JSON with the following structure. IMPORTANT: All values must be plain text strings with proper formatting - use newlines (\\n) for line breaks within strings. Do NOT use arrays or lists - format everything as readable prose or bullet points within a single string.

{{
    "lp_summary": "2-3 sentence summary of who this LP is and what they care about.",

    "opening_hook": "A compelling 2-3 sentence opening that immediately connects Bramble to this LP's interests.",

    "thesis_framing": "How to frame Bramble's investment thesis for this LP. Which of the 3 themes (Sustainable Production, Health & Nutrition, Waste Reduction) to emphasise and why. Write 1-2 paragraphs as flowing prose.",

    "tailwinds_emphasis": "Which market tailwinds to highlight. Format as:\\n\\n**Tailwind 1 Name**: Explanation of relevance to this LP...\\n\\n**Tailwind 2 Name**: Explanation...\\n\\n**Tailwind 3 Name**: Explanation...",

    "team_highlights": "Which team members and advisors to spotlight. Format as:\\n\\n**Person Name (Role)**: Why they're relevant to this LP...\\n\\n**Person Name**: Why relevant...\\n\\n(Pick 3-4 most relevant)",

    "value_add_framing": "How to frame Bramble's value-add for this LP. What aspects of the advisory/support model matter most to them? Write as flowing prose, 1-2 paragraphs.",

    "anticipated_questions": "Format as:\\n\\n**Q: Question they might ask?**\\n\\nPossible Answer: Suggested answer...\\n\\n**Q: Another question?**\\n\\nPossible Answer: Answer...\\n\\n(Include 3-5 questions)",

    "conversation_starters": "Format as:\\n\\n1. First conversation starter or question to ask them...\\n\\n2. Second conversation starter...\\n\\n3. Third conversation starter...",

    "risks_to_address": "Format as:\\n\\n**Concern 1 Title**\\nExplanation and how to address it...\\n\\n**Concern 2 Title**\\nExplanation and how to address it...\\n\\n(Include 2-4 potential concerns with clear line breaks between each)"
}}

Return ONLY valid JSON, no other text."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text

        # Parse JSON (handle potential markdown wrapping)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content)

    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse response as JSON: {e}", "raw_response": content}
    except Exception as e:
        return {"error": str(e)}


def format_pitch_output(lp_name: str, research: dict, pitch: dict) -> str:
    """Format the personalized pitch as readable markdown."""

    output = f"""# Bramble Investments - Personalised Pitch for {lp_name}
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

---

## LP Profile Summary

{pitch.get('lp_summary', 'N/A')}

---

## Opening Hook

> {pitch.get('opening_hook', 'N/A')}

---

## Investment Thesis Framing

{pitch.get('thesis_framing', 'N/A')}

---

## Key Market Tailwinds to Emphasise

{pitch.get('tailwinds_emphasis', 'N/A')}

---

## Team & Advisors to Feature

{pitch.get('team_highlights', 'N/A')}

---

## Value-Add Framing

{pitch.get('value_add_framing', 'N/A')}

---

## Anticipated Questions & Answers

{pitch.get('anticipated_questions', 'N/A')}

---

## Conversation Starters

{pitch.get('conversation_starters', 'N/A')}

---

## Potential Concerns to Address

{pitch.get('risks_to_address', 'N/A')}

---

## Research Notes

<details>
<summary>Click to expand full LP research</summary>

{research.get('research', 'No research available')}

</details>
"""
    return output


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate personalised LP pitch content for Bramble Investments"
    )
    parser.add_argument(
        "lp_name",
        help="Name of the LP/investor to research and personalise for"
    )
    parser.add_argument(
        "--context", "-c",
        default="",
        help="Additional context about the LP or meeting"
    )
    parser.add_argument(
        "--notes", "-n",
        default="",
        help="Additional notes from the team to incorporate"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (default: prints to stdout)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted markdown"
    )

    args = parser.parse_args()

    print(f"Researching {args.lp_name}...", file=sys.stderr)
    research = research_lp(args.lp_name, args.context)

    if research.get("error"):
        print(f"Research error: {research['error']}", file=sys.stderr)
        if not research.get("research"):
            sys.exit(1)

    print(f"Generating personalised pitch...", file=sys.stderr)
    pitch = generate_personalized_pitch(args.lp_name, research.get("research", ""), args.notes)

    if pitch.get("error"):
        print(f"Pitch generation error: {pitch['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        output = json.dumps({"research": research, "pitch": pitch}, indent=2)
    else:
        output = format_pitch_output(args.lp_name, research, pitch)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
