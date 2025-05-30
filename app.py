import streamlit as st
import requests
from fpdf import FPDF
import base64

st.set_page_config(page_title="Escape Planner", page_icon="🧠")
st.title("🧠 Quit My Job Escape Planner")
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


def log_email_to_mailerlite(email):
    url = "https://api.mailerlite.com/api/v2/groups/{}/subscribers".format(
        st.secrets["MAILERLITE_GROUP_ID"]
    )
    headers = {
        "Content-Type": "application/json",
        "X-MailerLite-ApiKey": st.secrets["MAILERLITE_API_KEY"],
    }
    payload = {"email": email, "name": "Escape Planner Lead"}
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code in [200, 201]


def log_email_to_google_sheets(email):
    webhook_url = st.secrets["GOOGLE_SHEETS_WEBHOOK_URL"]
    payload = {"email": email}
    try:
        response = requests.post(webhook_url, json=payload)
        return response.status_code == 200
    except:
        return False


if submitted:
    with st.spinner("Crafting your escape plan..."):
        try:
            full_prompt = prompt_template.format(
                job=job, income=income, skills=skills, savings=savings, goal=goal
            )

            headers = {
                "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
                "Content-Type": "application/json",
            }

            data = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": full_prompt},
                ],
                "temperature": 0.7,
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
            )

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    plan = result["choices"][0]["message"]["content"]
                    st.success("Here’s your personalized 90-day plan:")
                    st.markdown(plan)

                    st.markdown("---")
                    st.subheader("📥 Download Your Plan as a PDF")
                    email = st.text_input("Enter your email to receive the PDF")
                    download_requested = st.button("📄 Get My PDF Plan")

                    if download_requested:
                        if "@" in email and "." in email:
                            pdf_bytes = create_pdf(plan)
                            log_email_to_mailerlite(email)
                            log_email_to_google_sheets(email)
                            download_button(pdf_bytes, "Quit-My-Job-Escape-Plan.pdf")
                            st.success(
                                "✅ PDF ready. Click the link above to download."
                            )
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
                else:
                    st.error("No response content returned.")
                    st.json(result)
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")
