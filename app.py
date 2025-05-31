import streamlit as st
import requests
from fpdf import FPDF
import base64

# ---------------------- Streamlit Page Setup ---------------------- #
st.set_page_config(page_title="EscapePlanner.AI", page_icon="🧠", layout="centered")

# ---------------------- Branding Colors ---------------------- #
PRIMARY_COLOR = "#00ADB5"
DARK_BG = "#222831"
LIGHT_TEXT = "#EEEEEE"
ACCENT = "#FFD369"

st.markdown(
    f"""
    <style>
    body {{ background-color: {DARK_BG}; color: {LIGHT_TEXT}; }}
    .stApp {{
        background-color: {DARK_BG};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {ACCENT};
    }}
    .css-1cpxqw2 {{ background-color: {PRIMARY_COLOR}; }}
    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: none;
        padding: 10px 16px;
        border-radius: 8px;
    }}
    .stButton>button:hover {{
        background-color: {ACCENT};
        color: black;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------- Logo + Hero ---------------------- #
st.image("https://i.imgur.com/zYIlgBl.png", width=120)  # Replace with your logo URL
st.title("🧠 EscapePlanner.AI")
st.markdown(
    """
<div style='font-size:18px;'>
Escape the 9–5 grind with a smart, AI-powered 90-day roadmap tailored to your skills, savings, and goals.
</div>
""",
    unsafe_allow_html=True,
)
st.markdown("---")

# ---------------------- Form ---------------------- #
with st.form("escape_plan_form"):
    job = st.text_input("Current Job Title")
    income = st.text_input("Monthly Income (USD)")
    skills = st.text_area("Your Skills (comma-separated)")
    savings = st.text_input("Approximate Savings (USD)")
    goal = st.text_area("Your Dream Career / Lifestyle")
    submitted = st.form_submit_button("🚀 Generate My Escape Plan")

# ---------------------- Prompt Template ---------------------- #
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


# ---------------------- PDF Generation ---------------------- #
def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line)
    return pdf.output(dest="S").encode("latin-1")  # type: ignore


# ---------------------- Email Logging ---------------------- #
def log_email_to_mailerlite(email):
    url = f"https://api.mailerlite.com/api/v2/groups/{st.secrets['MAILERLITE_GROUP_ID']}/subscribers"
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


# ---------------------- Generate Plan ---------------------- #
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

            result = response.json()
            if response.status_code == 200 and "choices" in result:
                plan = result["choices"][0]["message"]["content"]
                st.session_state["plan"] = plan

                st.success("✅ Here’s your personalized 90-day plan:")
                st.markdown(plan)
                st.markdown("---")

                # 📥 Download Section
                st.subheader("📥 Download Your Plan as PDF")
                email = st.text_input("Enter your email to receive the PDF")
                if st.button("📄 Download My Plan"):
                    if "@" in email and "." in email:
                        pdf_bytes = create_pdf(plan)
                        log_email_to_mailerlite(email)
                        log_email_to_google_sheets(email)

                        b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/octet-stream;base64,{b64}" download="EscapePlan.pdf"><button>📥 Download Now</button></a>'
                        st.markdown(href, unsafe_allow_html=True)
                        st.success("✅ PDF ready. Click the button to download.")
                    else:
                        st.error("Please enter a valid email.")

                # CTA banners
                st.markdown("---")
                st.markdown(
                    f'<div style="background-color:{PRIMARY_COLOR};padding:15px;border-radius:10px;">'
                    f'<h3 style="color:white;">🎁 Upgrade to the Ultimate Quit Kit</h3>'
                    f'<a style="color:black;" href="https://gumroad.com/l/quitkit" target="_blank">Only $29 – Actionable templates, guides, and coaching insights!</a>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="background-color:{ACCENT};padding:15px;border-radius:10px;margin-top:15px;">'
                    f'<h3 style="color:black;">📬 Join the Escape Newsletter</h3>'
                    f'<a href="https://subscribepage.io/escape-plan" target="_blank">Get tools, tips, and income ideas every week.</a>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.error("Something went wrong. Please try again.")
                st.json(result)
        except Exception as e:
            st.error(f"Error: {e}")
