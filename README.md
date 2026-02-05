# Bramble LP Pitch Personalization Tool

Generate personalised pitch content for LP meetings based on deep research.

## What it does

1. **Researches the LP** via Perplexity - investment history, focus areas, values, decision makers
2. **Analyses the fit** - identifies which aspects of Bramble resonate with this LP
3. **Generates tailored content** for each pitch section:
   - Opening hook
   - Investment thesis framing (which themes to emphasise)
   - Market tailwinds to highlight
   - Portfolio companies to feature
   - Team/advisors to spotlight
   - Value-add framing
   - Anticipated Q&A
   - Conversation starters
   - Concerns to address

## Usage

### Command Line

```bash
# Basic usage
python lp_pitch.py "Holland & Barrett"

# With additional context
python lp_pitch.py "Wellcome Trust" --context "Met at Impact Week, interested in health tech"

# Save to file
python lp_pitch.py "Blue Horizon" --output pitch_blue_horizon.md

# Output as JSON
python lp_pitch.py "Balderton Capital" --json
```

### Streamlit App

```bash
streamlit run streamlit_app.py
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure API keys are available (checks in order):
   - Environment variables: `ANTHROPIC_API_KEY`, `PERPLEXITY_API_KEY`
   - `~/vc_screen_public/.secrets.toml`
   - `~/.api_key`, `~/.perplexity_key`

## Output

The tool produces **text content** for personalising your pitch - not a complete PDF deck. Use the output to:

- Update talking points before meetings
- Customise relevant slides in your master deck
- Prepare for Q&A
- Build rapport with LP-specific conversation starters
