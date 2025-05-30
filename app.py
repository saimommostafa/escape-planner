# 🔧 Quit My Job Escape Planner – AI Agent Prototype (Streamlit + Mixtral via Groq)

import streamlit as st
import requests
from fpdf import FPDF
import base64

# Load secrets from Streamlit's secrets management
st.set_page_config(page_title="Escape Planner", page_icon="🧧")
# Ensure you have set these in your Streamlit secrets.toml file
# [secrets.toml]

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.title("🧭 Quit My Job Escape Planner")
st.markdown("""
This AI agent helps you build a personalized 90-day escape plan from your 9–5 job.
Fill in your details and get a tailored roadmap you can follow to quit your job with confidence.
""")

with st.form("escape_plan_form"):
    job = st.text_input("Current Job Title")
    income = st.text_input("Monthly Income (USD)")
    skills = st.text_area("Your Skills (comma-separated)")
    savings = st.text_input("Approximate Savings (USD)")
    goal = st.text_area("Your Dream Career / Lifestyle")
    submitted = st.form_submit_button("Generate My Escape Plan")

prompt_template = """
You are a career transition coach and financial strategist. A user wants to quit their job and escape their 9–5 life.

Create a detailed, 90-day personalized escape plan based on these details:
- Current Job: {job}
- Monthly Income: {income}
- Skills: {skills}
- Savings: {savings}
- Goal: {goal}

The plan should include:
1. Side hustle or income source ideas based on their skills
2. Weekly action steps
3. Budget recommendations
4. Motivation tips
5. Tools/resources to use

Respond in a motivational and encouraging tone.
"""


def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line)
    return pdf.output(dest="S")


def download_button(pdf_bytes, filename):
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📄 Download Your Plan as PDF</a>'
    st.markdown(href, unsafe_allow_html=True)


def get_mixtral_response(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


if submitted:
    with st.spinner("Crafting your escape plan..."):
        try:
            full_prompt = prompt_template.format(
                job=job, income=income, skills=skills, savings=savings, goal=goal
            )
            plan = get_mixtral_response(full_prompt)
            st.success("Here’s your personalized 90-day plan:")
            st.markdown(plan)

            st.markdown("---")
            st.subheader("📥 Download Your Plan as a PDF")

            email = st.text_input("Enter your email to receive the PDF")
            download_requested = st.button("📄 Get My PDF Plan")

            if download_requested:
                if "@" in email and "." in email:
                    pdf_bytes = create_pdf(plan)
                    download_button(pdf_bytes, "Quit-My-Job-Escape-Plan.pdf")
                    st.success("✅ PDF ready. Click the link above to download.")
                else:
                    st.error("Please enter a valid email address.")

            st.markdown(
                "[🚀 Upgrade to the Ultimate Quit Kit – $29](https://gumroad.com/l/quitkit)",
                unsafe_allow_html=True,
            )
            st.markdown(
                "[📬 Join the Escape Newsletter](https://subscribepage.io/escape-plan)",
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Error: {e}")
