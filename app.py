import streamlit as st
from fpdf import FPDF
import base64
import gspread
from google.oauth2.service_account import Credentials
import datetime
import requests

# ---------------------------
# 🔧 Page Configuration
# ---------------------------
st.set_page_config(
    page_title="EscapePlanner.AI",
    page_icon="logo.png",  # Ensure logo.png exists in the same directory
    layout="centered",
)

# ---------------------------
# 🌗 Theme Toggle
# ---------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme = st.radio("Choose Theme:", ["dark", "light"], horizontal=True)

# ---------------------------
# 🎨 Dynamic Theme Styling
# ---------------------------
if theme == "dark":
    primary_color = "#ff6b6b"
    background = "#121212"
    surface = "#1e2127"
    text = "#ffffff"
else:
    primary_color = "#ff6b6b"
    background = "#ffffff"
    surface = "#f4f4f4"
    text = "#222222"

st.markdown(
    f"""
    <style>
    body {{
        background-color: {background};
        color: {text};
        font-family: 'Segoe UI', sans-serif;
    }}
    .hero {{
        background-color: {surface};
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.2);
    }}
    .cta-button {{
        background-color: {primary_color};
        color: white;
        padding: 0.8rem 1.4rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }}
    .faq {{
        background-color: {surface};
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# 🧠 Hero Section
# ---------------------------
st.markdown(
    """
<div class="hero">
    <img src="logo.png" width="80">
    <h1>🧠 EscapePlanner.AI</h1>
    <p><strong>Quit your 9–5 job in 90 days.</strong><br>
    A free AI agent that builds a personalized roadmap based on your skills, savings, and timeline.</p>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# 🔄 Multi-step Form
# ---------------------------
st.subheader("🔄 Let's build your Escape Plan")

with st.form("escape_form"):
    email = st.text_input("📬 Your Email")
    skills = st.multiselect(
        "🛠 What skills do you currently have?",
        ["Writing", "Design", "Marketing", "Programming", "Teaching", "Sales"],
    )
    savings = st.radio(
        "💰 How much savings do you currently have?",
        ["<$100", "$100–$500", "$500–$1000", "$1000+"],
    )
    goal = st.selectbox(
        "🎯 Your escape timeline goal?", ["30 Days", "60 Days", "90 Days"]
    )
    hustle = st.radio(
        "🚀 Preferred side hustle path:",
        ["Freelancing", "Digital Products", "Affiliate Marketing", "Coaching"],
    )
    submitted = st.form_submit_button("📥 Generate My Plan")

# ---------------------------
# 📄 Handle Submission
# ---------------------------
if submitted:
    if not email:
        st.warning("Please enter your email.")
    else:
        try:
            # Generate PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.set_title("Escape Plan")

            pdf.cell(200, 10, "Your Personalized Escape Plan", ln=True, align="C")
            pdf.cell(200, 10, f"Email: {email}", ln=True)
            pdf.cell(200, 10, f"Timeline: {goal}", ln=True)
            pdf.cell(200, 10, f"Savings: {savings}", ln=True)
            pdf.cell(200, 10, f"Preferred Hustle: {hustle}", ln=True)
            pdf.cell(200, 10, "Recommended Steps:", ln=True)
            pdf.multi_cell(
                0,
                10,
                f"""
Step 1: Upskill in {", ".join(skills)} through free resources.
Step 2: Start building a micro-offer around {hustle}.
Step 3: Allocate savings to setup minimal tools needed.
Step 4: Replace your income in {goal} through consistent action.
            """,
            )
            file_name = "escape_plan.pdf"
            pdf.output(file_name)

            # Download link
            with open(file_name, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                st.markdown(
                    f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="EscapePlan.pdf" class="cta-button">📄 Download Your Plan</a>',
                    unsafe_allow_html=True,
                )

            # 📊 Log to Google Sheets
            try:
                scopes = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ]
                creds = Credentials.from_service_account_file(
                    "secrets.json", scopes=scopes
                )
                client = gspread.authorize(creds)
                sheet = client.open("EscapePlannerUsers").sheet1
                sheet.append_row(
                    [
                        str(datetime.datetime.now()),
                        email,
                        ", ".join(skills),
                        savings,
                        goal,
                        hustle,
                    ]
                )
            except Exception as e:
                st.warning(f"⚠️ Could not log to Google Sheets: {e}")

            # MailerLite (Optional Placeholder)
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {st.secrets['mailerlite_api_key']}",
                }
                data = {"email": email, "groups": [st.secrets["mailerlite_group_id"]]}
                requests.post(
                    "https://api.mailerlite.com/api/v2/subscribers",
                    headers=headers,
                    json=data,
                )
            except Exception as e:
                st.warning(f"MailerLite error: {e}")

            st.success("🎉 Your personalized plan has been generated!")
            st.markdown("---")

            # Native CTA Buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📬 Join Newsletter"):
                    st.markdown(
                        "[Click here to subscribe](https://subscribepage.io/escape-plan)",
                        unsafe_allow_html=True,
                    )
            with col2:
                if st.button("🚀 Upgrade (Gumroad)"):
                    st.markdown(
                        "[Upgrade now](https://gumroad.com/l/quitkit)",
                        unsafe_allow_html=True,
                    )

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# ---------------------------
# 💬 Testimonials
# ---------------------------
st.markdown("### 💬 Testimonials")
st.markdown(
    """
<div class="faq">
<strong>“I followed the plan and started freelancing within 3 weeks!”</strong><br>- Mike, USA
</div>
<div class="faq">
<strong>“This free tool helped me validate my idea before quitting.”</strong><br>- Nicole, USA
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# ❓ FAQs Section
# ---------------------------
st.markdown("### ❓ FAQs")
st.markdown(
    """
<div class="faq"><strong>Is this really free?</strong><br>Yes! 100% free to use, no credit card needed.</div>
<div class="faq"><strong>Can I trust the plan?</strong><br>It's AI-generated based on your inputs. Customize it as needed.</div>
<div class="faq"><strong>Do I need to install anything?</strong><br>Nope. Just use it in your browser.</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# 📈 Free Analytics: Splitbee
# ---------------------------
st.markdown(
    """
<script async src="https://cdn.splitbee.io/sb.js"></script>
""",
    unsafe_allow_html=True,
)
