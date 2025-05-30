import streamlit as st
import requests
from fpdf import FPDF
import base64

st.set_page_config(
    page_title="Quit My Job Escape Planner", page_icon="🧠", layout="centered"
)
st.markdown(
    """
    <style>
        body { background-color: #0F172A; color: #FFFFFF; }
        .stButton>button { background-color: #6366F1; color: white; border-radius: 8px; }
        .stTextInput>div>div>input, .stTextArea>div>textarea {
            background-color: #1E293B;
            color: white;
            border-radius: 6px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧠 Quit My Job Escape Planner")
st.markdown("**A personalized 90-day roadmap to escape your 9–5 job.**")
st.markdown("🚀 [Get the Ultimate Quit Kit](https://your-gumroad-link.com)")
st.markdown("---")

with st.form("escape_plan_form"):
    job = st.text_input("Current Job Title")
    income = st.text_input("Monthly Income (USD)")
    skills = st.text_area("Your Skills (comma-separated)")
    savings = st.text_input("Approximate Savings (USD)")
    goal = st.text_area("Your Dream Career / Lifestyle")
    submitted = st.form_submit_button("Generate My Escape Plan")

prompt_template = """
You are a career transition coach and financial strategist. A user wants to quit their job and escape their 9–5 life.
Create a detailed, 90-day personalized escape plan based on:
- Current Job: {job}
- Monthly Income: {income}
- Skills: {skills}
- Savings: {savings}
- Goal: {goal}
Include:
1. Side hustle ideas based on their skills
2. Weekly action steps
3. Budget tips
4. Motivation advice
5. Tools/resources to use
Tone: Motivational and practical.
"""


def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line)
    return pdf.output(dest="S").encode("latin-1")


def download_button(pdf_bytes, filename):
    st.download_button(
        label="📄 Download Your Plan as PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
    )


def log_email_to_mailerlite(email):
    url = f"https://api.mailerlite.com/api/v2/groups/{st.secrets['MAILERLITE_GROUP_ID']}/subscribers"
    headers = {
        "Content-Type": "application/json",
        "X-MailerLite-ApiKey": st.secrets["MAILERLITE_API_KEY"],
    }
    payload = {"email": email, "name": "Escape Planner Lead"}
    response = requests.post(url, json=payload, headers=headers)
    return response.ok


def log_email_to_google_sheets(email):
    webhook_url = st.secrets["GOOGLE_SHEETS_WEBHOOK_URL"]
    payload = {"email": email}
    try:
        response = requests.post(webhook_url, json=payload)
        return response.ok
    except:
        return False


if submitted:
    st.session_state.full_prompt = prompt_template.format(
        job=job, income=income, skills=skills, savings=savings, goal=goal
    )
    with st.spinner("Crafting your escape plan..."):
        headers = {
            "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": st.session_state.full_prompt},
            ],
            "temperature": 0.7,
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
        )
        if response.status_code == 200 and "choices" in response.json():
            result = response.json()
            plan = result["choices"][0]["message"]["content"]
            st.session_state.plan = plan
            st.success("✅ Your personalized plan is ready!")
            st.markdown(plan)
            st.markdown("---")
            email = st.text_input("📧 Enter your email to receive your plan")
            download_requested = st.button("📩 Get My Plan")
            if download_requested and "@" in email and "." in email:
                pdf_bytes = create_pdf(plan)
                log_email_to_mailerlite(email)
                log_email_to_google_sheets(email)
                download_button(pdf_bytes, "Quit-My-Job-Escape-Plan.pdf")
        else:
            st.error("Something went wrong. Please try again.")
# The code above is a Streamlit application that helps users create a personalized escape plan to quit their job.
# It collects user input about their current job, income, skills, savings, and career goals.
# After submitting the form, it generates a detailed 90-day escape plan using the Groq API.
# The plan includes side hustle ideas, weekly action steps, budget tips, motivation advice, and recommended tools/resources.
# The user can then download the plan as a PDF and optionally log their email to MailerLite and Google Sheets for follow-up.
# The application is styled with custom CSS for a better user experience.
