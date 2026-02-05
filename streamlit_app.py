#!/usr/bin/env python3
"""
Bramble LP Pitch Personalization Tool - Streamlit Interface
"""

import streamlit as st
import os
from datetime import datetime
from lp_pitch import research_lp, generate_personalized_pitch, format_pitch_output, BRAMBLE_PITCH

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Bramble LP Pitch Tool",
    page_icon="🌿",
    layout="wide"
)

# =============================================================================
# STYLING
# =============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #2d5016;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d5016;
        border-bottom: 2px solid #c9a227;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    .highlight-box {
        background-color: #f8f6f0;
        border-left: 4px solid #c9a227;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #2d5016;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================

st.markdown('<p class="main-header">Bramble LP Pitch Tool</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate personalised pitch content for LP meetings</p>', unsafe_allow_html=True)

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("### About")
    st.markdown("""
    This tool helps prepare personalised pitches for LP meetings by:

    1. **Researching** the LP via Perplexity
    2. **Analysing** what aspects of Bramble resonate
    3. **Generating** tailored talking points

    The output is text for key sections - not a complete deck.
    """)

    st.markdown("---")
    st.markdown("### Recent Pitches")

    # List saved pitches
    output_dir = "pitches"
    if os.path.exists(output_dir):
        files = sorted(os.listdir(output_dir), reverse=True)[:5]
        for f in files:
            if f.endswith(".md"):
                st.markdown(f"- {f.replace('.md', '').replace('_', ' ')}")
    else:
        st.markdown("*No saved pitches yet*")

# =============================================================================
# MAIN INPUT
# =============================================================================

with st.form("pitch_form"):
    lp_name = st.text_input(
        "LP / Investor Name",
        placeholder="e.g., Family Office X, Pension Fund Y, Strategic Investor Z",
        help="Enter the name of the LP you're meeting with"
    )

    context = st.text_area(
        "Notes & Context (optional)",
        placeholder="e.g., Family office focused on health tech, met at a conference, introduced by Michael Jary, interested in gut health thesis, concerned about fund size...",
        help="Any context to help research and personalise the pitch"
    )

    submitted = st.form_submit_button("Generate Personalised Pitch", type="primary", use_container_width=True)

# =============================================================================
# GENERATE
# =============================================================================

if submitted:
    if not lp_name:
        st.error("Please enter an LP name")
    else:
        # Research phase
        with st.status("Researching LP...", expanded=True) as status:
            st.write(f"Querying Perplexity for information on {lp_name}...")
            research = research_lp(lp_name, context)

            if research.get("error"):
                st.warning(f"Research note: {research['error']}")

            if research.get("research"):
                st.write("Research complete!")
                status.update(label="Research complete", state="complete")
            else:
                st.error("Failed to retrieve research")
                st.stop()

        # Generation phase
        with st.status("Generating personalised pitch...", expanded=True) as status:
            st.write("Analysing LP profile and generating tailored content...")
            pitch = generate_personalized_pitch(lp_name, research.get("research", ""), context)

            if pitch.get("error"):
                st.error(f"Generation error: {pitch['error']}")
                st.stop()

            status.update(label="Pitch generated!", state="complete")

        # Store in session state
        st.session_state.research = research
        st.session_state.pitch = pitch
        st.session_state.lp_name = lp_name

# =============================================================================
# DISPLAY RESULTS
# =============================================================================

if "pitch" in st.session_state:
    pitch = st.session_state.pitch
    research = st.session_state.research
    lp_name = st.session_state.lp_name

    st.markdown("---")
    st.markdown(f'<p class="section-header">Personalised Pitch for {lp_name}</p>', unsafe_allow_html=True)

    # LP Summary
    st.markdown("### LP Profile")
    st.markdown(f'<div class="highlight-box">{pitch.get("lp_summary", "N/A")}</div>', unsafe_allow_html=True)

    # Opening Hook
    st.markdown("### Opening Hook")
    st.info(pitch.get("opening_hook", "N/A"))

    # Two columns for main content
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Thesis Framing")
        st.markdown(pitch.get("thesis_framing", "N/A"))

        st.markdown("### Value-Add Framing")
        st.markdown(pitch.get("value_add_framing", "N/A"))

    with col2:
        st.markdown("### Market Tailwinds")
        st.markdown(pitch.get("tailwinds_emphasis", "N/A"))

        st.markdown("### Team to Feature")
        st.markdown(pitch.get("team_highlights", "N/A"))

    # Full width sections
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Anticipated Questions")
        st.markdown(pitch.get("anticipated_questions", "N/A"))

    with col2:
        st.markdown("### Conversation Starters")
        st.markdown(pitch.get("conversation_starters", "N/A"))

    st.markdown("### Potential Concerns")
    st.warning(pitch.get("risks_to_address", "N/A"))

    # Research details (expandable)
    with st.expander("View Full Research"):
        st.markdown(research.get("research", "No research available"))

    # Download options
    st.markdown("---")
    st.markdown("### Export")

    # Generate markdown output
    md_output = format_pitch_output(lp_name, research, pitch)

    st.download_button(
        "Download as Markdown",
        md_output,
        file_name=f"bramble_pitch_{lp_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md",
        mime="text/markdown",
        use_container_width=True
    )

# =============================================================================
# REFERENCE SECTION
# =============================================================================

with st.expander("View Bramble Core Pitch (Reference)"):
    st.markdown(BRAMBLE_PITCH)
