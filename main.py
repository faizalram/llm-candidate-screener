import streamlit as st
from agents.orchestrator import Orchestrator
import plotly.express as px
import os
import re

# Initialize the Orchestrator
orchestrator = Orchestrator()

# Set Page Configuration
st.set_page_config(
    page_title="LLM-powered Candidate Screener",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS for Styling
st.markdown("""
    <style>
        .stApp {
            background-color: #f7f8fa;
        }
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #2c3e50;
        }
        .subheader {
            font-size: 20px;
            font-weight: bold;
            color: #34495e;
        }
        .metric {
            font-size: 24px;
            font-weight: bold;
            color: #16a085;
        }
        /* Add dark text color for all content */
        .stMarkdown, .stText {
            color: #2c3e50 !important;
        }
        /* Style for success messages */
        .stSuccess {
            color: #155724 !important;
            background-color: #d4edda !important;
            border-color: #c3e6cb !important;
        }
        /* Style for warning messages */
        .stWarning {
            color: #856404 !important;
            background-color: #fff3cd !important;
            border-color: #ffeeba !important;
        }
        /* Style for info messages */
        .stInfo {
            color: #004085 !important;
            background-color: #cce5ff !important;
            border-color: #b8daff !important;
        }
        /* Style for bullet points and regular text */
        p {
            color: #2c3e50 !important;
        }
        /* Style for links */
        a {
            color: #2980b9 !important;
        }
        /* Style for headers */
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50 !important;
        }
        /* Style specifically for sidebar */
        [data-testid="stSidebarNav"] {
            background-color: #2c3e50;
        }
        .css-17lntkn {
            color: white !important;
        }
        .css-pkbazv {
            color: white !important;
        }
        /* Make sure all sidebar text color is light */
        [data-testid="stSidebar"] .css-17lntkn {
            color: white !important;
        }
        [data-testid="stSidebar"] h1 {
            color: white !important;
        }
        /* Style for file uploader text in sidebar */
        [data-testid="stSidebar"] .css-184tjsw p {
            color: white !important;
        }
        [data-testid="stSidebar"] .css-1dhfpht p {
            color: white !important;
        }
        /* Additional sidebar text elements */
        [data-testid="stSidebar"] label {
            color: white !important;
        }
        [data-testid="stSidebar"] .stMarkdown {
            color: white !important;
        }
        [data-testid="stSidebar"] p {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# Main Title
st.markdown('<div class="title">Welcome to LLM-powered Candidate Screener</div>', unsafe_allow_html=True)
st.sidebar.image("data/logo.png", use_container_width=True)
st.sidebar.markdown('<h1 style="color: white;">Upload Resume</h1>', unsafe_allow_html=True)

# Step 1: File Upload with light colored text
uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF)", type=["pdf"])

if uploaded_file:
    st.sidebar.success("Resume uploaded successfully! ✅")

    # Process Resume Button
    if st.sidebar.button("Process Resume"):
        with st.spinner("Analyzing Resume..."):
            resume_path = f"temp_{uploaded_file.name}"
            with open(resume_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Define job_list_path
            job_list_path = os.path.join("data", "job_list.json")

            # Orchestrator Call with both parameters
            result = orchestrator.process_resume(resume_path, job_list_path)

        if "error" in result:
            st.error(result["error"])
        else:
            # Tab Layout
            tab1, tab2, tab3, tab4 = st.tabs(
                ["📝 Analysis", "💼 Job Matches", "📊 Screening", "✅ Final Recommendation"]
            )

            with tab1:
                st.markdown('<div class="subheader">Analysis Results</div>', unsafe_allow_html=True)
                strengths = result["analysis_results"].get("strengths", [])
                weaknesses = result["analysis_results"].get("weaknesses", [])
                suggestions = result["analysis_results"].get("suggestions", [])
                confidence_score = result["analysis_results"].get("confidence_score", 0.0)

                st.write("### Strengths:")
                if strengths:
                    for strength in strengths:
                        points = re.split(r'\d+\.\s*', strength)
                        for point in points:
                            if point.strip():
                                st.success(f"{point.strip()}")
                else:
                    st.success("No strengths identified.")

                st.write("### Weaknesses:")
                if weaknesses:
                    for weakness in weaknesses:
                        points = re.split(r'\d+\.\s*', weakness)
                        for point in points:
                            if point.strip():
                                st.warning(f"{point.strip()}")
                else:
                    st.warning("No weaknesses identified.")

                st.write("### Suggestions:")
                if suggestions:
                    for suggestion in suggestions:
                        points = re.split(r'\d+\.\s*', suggestion)
                        for point in points:
                            if point.strip():
                                st.info(f"{point.strip()}")
                else:
                    st.info("No suggestions available.")

                st.write("### Confidence Score:")
                st.progress(confidence_score)

            with tab2:
                st.markdown('<div class="subheader">Job Matches</div>', unsafe_allow_html=True)
                job_matches = result["matched_jobs"]

                if job_matches:
                    for job in job_matches:
                        st.markdown(f"**{job['title']}**")
                        st.write(f"Match Score: {job.get('confidence_score', 0.0)}")
                        if job.get('reasoning'):
                            reasoning_points = job['reasoning'].split(". ")
                            for point in reasoning_points:
                                st.write(f"- {point.strip()}")
                        st.markdown("---")
                else:
                    st.warning("No job matches found.")

            with tab3:
                st.markdown('<div class="subheader">Screening Results</div>', unsafe_allow_html=True)
                screening = result["screening_results"]

                metrics = {
                    "Qualification Alignment": screening.get("qualification_alignment_score", 0.0),
                    "Experience Relevance": screening.get("experience_relevance_score", 0.0),
                    "Skills Match": screening.get("skills_match_score", 0.0),
                    "Red Flags": screening.get("potential_red_flags_score", 0.0),
                }
                fig = px.line_polar(
                    r=list(metrics.values()),
                    theta=list(metrics.keys()),
                    line_close=True,
                    range_r=[0, 1],
                    title="Screening Metrics",
                )
                st.plotly_chart(fig, use_container_width=True)

            with tab4:
                st.markdown('<div class="subheader">Final Recommendation</div>', unsafe_allow_html=True)
                recommendations = result["recommendations"]
                
                st.write("### Summary")
                summary_points = recommendations.get("recommendation_summary", "No summary available.").split(". ")
                for point in summary_points:
                    st.write(f"- {point.strip()}")
                
                st.write("### Top Matched Job")
                st.success(recommendations.get("top_matched_job", "No top match available."))
                
                st.write("### Additional Notes")
                notes_points = recommendations.get("additional_notes", "No additional notes available.").split(". ")
                for point in notes_points:
                    st.info(f"- {point.strip()}")

        # Clean up
        os.remove(resume_path)

else:
    st.info("Please upload a resume to begin.")