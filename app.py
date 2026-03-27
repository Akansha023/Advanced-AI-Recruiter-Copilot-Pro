import os
"""
AI Recruiter Copilot — Upgraded Main Application
Features: Step-by-step spinners, JSON score breakdown, skill matching,
          multi-resume comparison, score explainer, final decision banner.
"""

import streamlit as st
import time
import json
from utils import (
    process_resume, retrieve_relevant_context, call_llm,
    call_llm_json, extract_skills_from_jd
)
import prompts

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Recruiter Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Header ── */
    .main-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .main-header h1 { color: #fff; font-size: 2.4rem; font-weight: 700; margin: 0; }
    .main-header p  { color: #a5b4fc; font-size: 1rem; margin: 0.5rem 0 1rem; }

    /* ── Badges ── */
    .badge {
        display: inline-block;
        background: rgba(99,102,241,0.25);
        color: #c7d2fe;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 600;
        margin: 3px;
        border: 1px solid rgba(165,180,252,0.3);
    }

    /* ── How-to card ── */
    .howto-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #1e3a5f 100%);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .howto-card h3 { color: #e0e7ff; font-size: 1rem; margin: 0 0 1rem; }
    .howto-section { margin-bottom: 1rem; }
    .howto-section h4 { color: #a5b4fc; font-size: 0.8rem; font-weight: 600;
                        text-transform: uppercase; letter-spacing: 0.06em; margin: 0 0 0.5rem; }
    .howto-item {
        display: flex; align-items: flex-start; gap: 10px;
        color: #cbd5e1; font-size: 0.85rem; line-height: 1.5; margin-bottom: 6px;
    }
    .howto-num {
        background: rgba(99,102,241,0.3); color: #c7d2fe;
        width: 22px; height: 22px; border-radius: 50%;
        font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        margin-top: 1px;
    }
    .howto-dot { color: #818cf8; flex-shrink: 0; margin-top: 3px; font-size: 0.9rem; }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; padding: 0.75rem 2rem !important;
        font-weight: 600 !important; font-size: 1rem !important;
        width: 100% !important; transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(79,70,229,0.4) !important;
    }

    /* ── Score card ── */
    .score-card {
        background: linear-gradient(135deg, #1e1b4b, #1e3a5f);
        border: 1px solid rgba(165,180,252,0.2);
        border-radius: 14px; padding: 1.5rem; margin-bottom: 1rem;
    }
    .score-big { font-size: 3rem; font-weight: 700; color: #818cf8; line-height: 1; }
    .score-label { color: #a5b4fc; font-size: 0.85rem; margin-top: 4px; }
    .rec-badge-hire   { background:#166534; color:#bbf7d0; padding:6px 16px;
                         border-radius:20px; font-size:0.85rem; font-weight:600; display:inline-block; }
    .rec-badge-strong { background:#1e3a8a; color:#bfdbfe; padding:6px 16px;
                         border-radius:20px; font-size:0.85rem; font-weight:600; display:inline-block; }
    .rec-badge-maybe  { background:#78350f; color:#fde68a; padding:6px 16px;
                         border-radius:20px; font-size:0.85rem; font-weight:600; display:inline-block; }
    .rec-badge-no     { background:#7f1d1d; color:#fecaca; padding:6px 16px;
                         border-radius:20px; font-size:0.85rem; font-weight:600; display:inline-block; }

    /* ── Decision banner ── */
    .decision-hire   { background:linear-gradient(135deg,#052e16,#14532d);
                        border:1px solid #166534; border-radius:12px; padding:1.2rem 1.5rem; margin:1rem 0; }
    .decision-strong { background:linear-gradient(135deg,#0c1445,#1e3a8a);
                        border:1px solid #1d4ed8; border-radius:12px; padding:1.2rem 1.5rem; margin:1rem 0; }
    .decision-maybe  { background:linear-gradient(135deg,#1c0a00,#78350f);
                        border:1px solid #92400e; border-radius:12px; padding:1.2rem 1.5rem; margin:1rem 0; }
    .decision-reject { background:linear-gradient(135deg,#1c0606,#7f1d1d);
                        border:1px solid #991b1b; border-radius:12px; padding:1.2rem 1.5rem; margin:1rem 0; }
    .decision-text { color:#fff; font-size:1rem; font-weight:600; margin:0; }
    .decision-reason { color:rgba(255,255,255,0.75); font-size:0.85rem; margin:4px 0 0; }

    /* ── Sidebar ── */
    .sidebar-info {
        background: #1e1b4b; border-radius: 10px; padding: 1rem;
        font-size: 0.83rem; color: #a5b4fc;
        border: 1px solid rgba(165,180,252,0.2);
    }
    .sidebar-info b { color: #e0e7ff; }

    /* ── Step tracker ── */
    .step-done { color: #4ade80; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="Enter your API key...",
        help="Get your free key at https://aistudio.google.com"
    )
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        st.success("✅ API Key set!")

    st.markdown("---")

    # ── HOW TO USE (inline in sidebar) ───────────────────────────────────
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. Upload candidate resume(s) as PDF
    2. Paste the job description
    3. Click **Analyze** and watch AI work step-by-step
    4. Review: Summary → Score → Skills → Questions → Decision
    """)

    st.markdown("---")
    st.markdown("### 🛠️ Tech Stack")
    for tech in ["Gemini 2.5 Flash (LLM)", "ChromaDB (Vector DB)",
                 "SentenceTransformers", "LangChain (Chunking)", "Streamlit (UI)"]:
        st.markdown(f"• {tech}")

    st.markdown("---")
    st.markdown("""
    <div class='sidebar-info'>
    💡 <b>100% Free Stack.</b><br>
    Gemini API has a generous free tier.<br>
    ChromaDB runs in-memory — no setup needed.
    </div>
    """, unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Recruiter Copilot</h1>
    <p>Intelligent resume analysis powered by Gemini AI + RAG pipeline</p>
    <div>
        <span class="badge">Gemini 2.5 Flash</span>
        <span class="badge">RAG Pipeline</span>
        <span class="badge">Vector Search</span>
        <span class="badge">Score Breakdown</span>
        <span class="badge">Skill Matching</span>
        <span class="badge">Free Stack</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── HOW-TO CARD (always visible) ─────────────────────────────────────────────
with st.expander("📌 What this tool does & how to use it", expanded=False):
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("""
        **🚀 What this tool does**
        - 📝 Summarizes candidate profile
        - ✅ Evaluates job fit with a scored breakdown
        - 🧩 Matches resume skills vs JD requirements
        - 💬 Generates targeted interview questions
        - 🧠 Explains *why* a score was given
        - 📌 Gives a final hire / reject recommendation
        """)

    with col_b:
        st.markdown("""
        **📌 How to use (Single mode)**
        1. Upload a candidate's resume (PDF)
        2. Paste the job description
        3. Click **Analyze Candidate**
        4. Watch the AI work step-by-step
        5. Review all insights in the tabs below
        """)

    with col_c:
        st.markdown("""
        **⚖️ How to use (Compare mode)**
        1. Switch to **Compare** mode above
        2. Upload 2–5 resumes at once
        3. Paste the shared job description
        4. Click **Compare All Candidates**
        5. See a ranked table with scores
        6. Pick the best fit instantly
        """)

    st.info("💡 **UX Goal:** AI feels like a structured evaluation system — not a magic black box. Every score is explained.", icon="ℹ️")


st.markdown("---")


# ─── Mode Selector ────────────────────────────────────────────────────────────
mode = st.radio(
    "Select Mode",
    ["🔍 Single Candidate Analysis", "⚖️ Compare Multiple Candidates"],
    horizontal=True
)

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# SINGLE CANDIDATE MODE
# ══════════════════════════════════════════════════════════════════════════════
if mode == "🔍 Single Candidate Analysis":

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📄 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload the candidate's resume in PDF format"
        )
        if uploaded_file:
            st.success(f"✅ Uploaded: {uploaded_file.name}")

    with col2:
        st.subheader("📋 Job Description")
        jd = st.text_area(
            "Paste the full job description here",
            height=180,
            placeholder="We are looking for a Senior Python Engineer with 5+ years experience..."
        )

    st.markdown("---")
    analyze_btn = st.button("🚀 Analyze Candidate", use_container_width=True)

    if analyze_btn:
        if not uploaded_file:
            st.error("⚠️ Please upload a resume PDF.")
        elif not jd.strip():
            st.error("⚠️ Please paste a job description.")
        elif not os.environ.get("GOOGLE_API_KEY", ""):
            st.error("⚠️ Please enter your Gemini API key in the sidebar.")
        else:
            # ── Step-by-step pipeline with individual spinners ─────────────
            step_log = st.empty()
            completed = []

            def log_step(msg):
                completed.append(f"✅ {msg}")
                step_log.markdown("\n\n".join(completed))

            raw_text, collection_name, context = None, None, None
            summary, sr, score_data, questions, why, decision_raw = (None,) * 6
            jd_skills, skill_match_result = None, None

            try:
                with st.spinner("🔍 Extracting text from resume PDF..."):
                    raw_text, collection_name = process_resume(uploaded_file)
                log_step("Resume extracted and indexed")

                with st.spinner("🧠 Understanding candidate profile..."):
                    context = retrieve_relevant_context(jd, collection_name)
                log_step("Candidate profile understood via semantic search")

                with st.spinner("🧩 Extracting required skills from job description..."):
                    jd_skills = extract_skills_from_jd(jd)
                log_step(f"Found {len(jd_skills)} required skills in JD")

                with st.spinner("✍️ Generating candidate summary..."):
                    summary = call_llm(prompts.summary_prompt(context))
                log_step("Summary generated")

                with st.spinner("🔍 Analyzing strengths & risks..."):
                    sr = call_llm(prompts.strengths_risks_prompt(context, jd))
                log_step("Strengths & risks analyzed")

                with st.spinner("🎯 Calculating fit score (JSON breakdown)..."):
                    score_data = call_llm_json(prompts.scoring_prompt(context, jd))
                log_step("Fit score calculated with breakdown")

                with st.spinner("🧩 Matching candidate skills vs JD..."):
                    skills_str = ", ".join(jd_skills)
                    skill_match_result = call_llm(prompts.skill_match_prompt(context, skills_str))
                log_step("Skill match analysis complete")

                with st.spinner("💬 Generating interview questions..."):
                    questions = call_llm(prompts.questions_prompt(context, jd))
                log_step("Interview questions generated")

                with st.spinner("🧠 Explaining the score..."):
                    why = call_llm(prompts.why_score_prompt(context, score_data))
                log_step("Score explanation ready")

                with st.spinner("📌 Making final recruiter decision..."):
                    decision_raw = call_llm(prompts.decision_prompt(context, score_data, jd))
                log_step("Final decision made")

                step_log.empty()

            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.info("💡 Make sure your API key is valid and the PDF is not password-protected.")
                st.stop()

            # ── RESULTS ───────────────────────────────────────────────────
            st.success("🎉 Analysis complete! Review all insights below.")
            st.markdown("---")

            # ── FINAL DECISION BANNER (top — most visible) ─────────────
            st.subheader("📌 Final Recruiter Recommendation")
            decision_line = decision_raw.strip()
            decision_label = ""
            reason_line = ""
            for line in decision_line.split("\n"):
                if line.startswith("DECISION:"):
                    decision_label = line.replace("DECISION:", "").strip()
                elif line.startswith("REASON:"):
                    reason_line = line.replace("REASON:", "").strip()

            dl = decision_label.lower()
            if "strong" in dl:
                css_class = "decision-strong"
                icon = "🌟"
            elif "hire" in dl:
                css_class = "decision-hire"
                icon = "✅"
            elif "consider" in dl or "maybe" in dl:
                css_class = "decision-maybe"
                icon = "🤔"
            else:
                css_class = "decision-reject"
                icon = "❌"

            st.markdown(f"""
            <div class="{css_class}">
                <p class="decision-text">{icon} {decision_label}</p>
                <p class="decision-reason">{reason_line}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # ── TABS ──────────────────────────────────────────────────────
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📌 Summary",
                "✅ Strengths & Risks",
                "🎯 Fit Score",
                "🧩 Skill Match",
                "💬 Questions",
                "🧠 Why This Score?"
            ])

            # ── TAB 1: SUMMARY ────────────────────────────────────────────
            with tab1:
                st.markdown("### Candidate Summary")
                st.markdown(summary)
                with st.expander("📄 View Raw Resume Text"):
                    st.text(raw_text[:3000] + ("..." if len(raw_text) > 3000 else ""))

            # ── TAB 2: STRENGTHS & RISKS ──────────────────────────────────
            with tab2:
                st.markdown("### Strengths & Risks Analysis")
                st.markdown(sr)

            # ── TAB 3: FIT SCORE (visual breakdown) ───────────────────────
            with tab3:
                st.markdown("### 🎯 Candidate Fit Score")

                if isinstance(score_data, dict):
                    # Big score + recommendation
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        final = score_data.get("Final Score", 0)
                        rec   = score_data.get("Recommendation", "")
                        st.markdown(f"""
                        <div class="score-card">
                            <div class="score-big">{final}<span style="font-size:1.2rem;color:#6366f1">/20</span></div>
                            <div class="score-label">Overall Fit Score</div>
                            <br/>
                        """, unsafe_allow_html=True)
                        rec_lower = rec.lower()
                        if "strong" in rec_lower:
                            st.markdown('<span class="rec-badge-strong">⭐ Strong Hire</span>', unsafe_allow_html=True)
                        elif "hire" in rec_lower:
                            st.markdown('<span class="rec-badge-hire">✅ Hire</span>', unsafe_allow_html=True)
                        elif "maybe" in rec_lower:
                            st.markdown('<span class="rec-badge-maybe">🤔 Maybe</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="rec-badge-no">❌ No Hire</span>', unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    with c2:
                        dims = [
                            ("🎓 Skill Match",    "Skill Match",    "Skill Match Reason"),
                            ("📅 Experience",     "Experience",     "Experience Reason"),
                            ("🏢 Job Stability",  "Stability",      "Stability Reason"),
                            ("🎯 Domain Fit",     "Domain",         "Domain Reason"),
                        ]
                        for label, key, reason_key in dims:
                            val    = score_data.get(key, 0)
                            reason = score_data.get(reason_key, "")
                            st.markdown(f"**{label}** — {val}/5")
                            st.progress(val / 5)
                            if reason:
                                st.caption(reason)

                    st.markdown("---")
                    overall_reason = score_data.get("Reason", "")
                    if overall_reason:
                        st.info(f"**Overall:** {overall_reason}")
                else:
                    st.warning("Score data could not be parsed. Raw response:")
                    st.code(str(score_data))

            # ── TAB 4: SKILL MATCH ────────────────────────────────────────
            with tab4:
                st.markdown("### 🧩 Skill Match Analysis")
                st.markdown(f"**Required skills extracted from JD:** `{', '.join(jd_skills)}`")
                st.markdown("---")
                st.markdown(skill_match_result)

            # ── TAB 5: INTERVIEW QUESTIONS ────────────────────────────────
            with tab5:
                st.markdown("### 💬 Interview Question Bank")
                st.markdown(questions)

            # ── TAB 6: WHY THIS SCORE ─────────────────────────────────────
            with tab6:
                st.markdown("### 🧠 Why This Score?")
                st.markdown("> *Plain-English explanation for your hiring team*")
                st.markdown(why)


# ══════════════════════════════════════════════════════════════════════════════
# COMPARE MODE
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("⚖️ Compare Multiple Candidates")
    st.info("Upload 2–5 resumes. The tool will score and rank them all against the same job description.")

    uploaded_files = st.file_uploader(
        "Upload Resumes (2–5 PDFs)",
        type=['pdf'],
        accept_multiple_files=True,
        help="Hold Ctrl/Cmd to select multiple files"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} resume(s) uploaded: {', '.join(f.name for f in uploaded_files)}")

    jd_compare = st.text_area(
        "📋 Shared Job Description",
        height=150,
        placeholder="Paste the job description that applies to all candidates..."
    )

    compare_btn = st.button("⚖️ Compare All Candidates", use_container_width=True)

    if compare_btn:
        if not uploaded_files or len(uploaded_files) < 2:
            st.error("⚠️ Please upload at least 2 resume PDFs.")
        elif not jd_compare.strip():
            st.error("⚠️ Please paste a job description.")
        elif not os.environ.get("GOOGLE_API_KEY", ""):
            st.error("⚠️ Please enter your Gemini API key in the sidebar.")
        else:
            results = []
            progress_bar = st.progress(0)
            status_text  = st.empty()

            for i, file in enumerate(uploaded_files):
                status_text.text(f"🔄 Analyzing {file.name} ({i+1}/{len(uploaded_files)})...")

                try:
                    with st.spinner(f"🔍 Extracting: {file.name}"):
                        _, collection_name = process_resume(file)

                    with st.spinner(f"🎯 Scoring: {file.name}"):
                        context   = retrieve_relevant_context(jd_compare, collection_name)
                        score_data = call_llm_json(prompts.scoring_prompt(context, jd_compare))
                        summary    = call_llm(prompts.summary_prompt(context))

                    results.append({
                        "name":     file.name.replace(".pdf", ""),
                        "score":    score_data.get("Final Score", 0),
                        "rec":      score_data.get("Recommendation", "—"),
                        "skill":    score_data.get("Skill Match", 0),
                        "exp":      score_data.get("Experience", 0),
                        "stab":     score_data.get("Stability", 0),
                        "domain":   score_data.get("Domain", 0),
                        "reason":   score_data.get("Reason", ""),
                        "summary":  summary,
                        "context":  context,
                    })
                except Exception as e:
                    st.warning(f"⚠️ Could not process {file.name}: {e}")

                progress_bar.progress((i + 1) / len(uploaded_files))

            status_text.empty()
            progress_bar.empty()

            if not results:
                st.error("No results could be generated.")
                st.stop()

            # Sort by score descending
            results.sort(key=lambda x: x["score"], reverse=True)

            st.success(f"✅ Comparison complete! Ranked {len(results)} candidates.")
            st.markdown("---")

            # ── RANKED TABLE ──────────────────────────────────────────────
            st.subheader("📊 Candidate Rankings")

            import pandas as pd
            df = pd.DataFrame([{
                "Rank":           f"#{i+1}",
                "Candidate":      r["name"],
                "Total Score":    f"{r['score']}/20",
                "Skill Match":    f"{r['skill']}/5",
                "Experience":     f"{r['exp']}/5",
                "Stability":      f"{r['stab']}/5",
                "Domain Fit":     f"{r['domain']}/5",
                "Recommendation": r["rec"],
            } for i, r in enumerate(results)])

            st.dataframe(df, use_container_width=True, hide_index=True)

            # ── PER-CANDIDATE DETAIL ──────────────────────────────────────
            st.markdown("---")
            st.subheader("🔍 Individual Summaries")

            for i, r in enumerate(results):
                with st.expander(f"#{i+1} — {r['name']} ({r['score']}/20 · {r['rec']})"):
                    st.markdown(r["summary"])
                    if r["reason"]:
                        st.info(r["reason"])

            # ── HEAD-TO-HEAD (top 2) ──────────────────────────────────────
            if len(results) >= 2:
                st.markdown("---")
                st.subheader("⚖️ Head-to-Head: Top 2 Candidates")
                with st.spinner("Generating head-to-head comparison..."):
                    comparison = call_llm(
                        prompts.compare_prompt(
                            results[0]["context"],
                            results[1]["context"],
                            jd_compare
                        )
                    )
                st.markdown(comparison)


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#718096; font-size:0.8rem; padding:1rem;'>
    Built with ❤️ using Gemini AI + RAG Pipeline &nbsp;|&nbsp;
    <a href='https://github.com' style='color:#818cf8;'>GitHub</a> &nbsp;|&nbsp;
    Stack: Streamlit · ChromaDB · SentenceTransformers · LangChain · Gemini 2.5 Flash
</div>
""", unsafe_allow_html=True)
