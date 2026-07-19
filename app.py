import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF
import re

# 1. PAGE CONFIG & BRANDING
st.set_page_config(page_title="Cognito AI Copilot", layout="wide", page_icon="🤖")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #ffffff; border-radius: 5px; border: 1px solid #eee; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #007bff; color: white; border: 1px solid #007bff; }
    div[data-testid="stMetricValue"] { color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Cognito AI Sales Intelligence")
st.write("Professional Audit & Automation Roadmap")

# 2. INPUTS
with st.sidebar:
    st.header("Business Profile")
    biz_name = st.text_input("Business Name")
    target_url = st.text_input("Website URL")
    city = st.text_input("City")
    
    st.divider()
    st.header("Settings")
    gemini_key = st.text_input("Gemini API Key", type="password").strip()
    google_key = st.text_input("PageSpeed API Key", type="password").strip()

# 3. LOGIC ENGINES
def get_tech_scores(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=SEO&category=PERFORMANCE&key={api_key}"
    try:
        r = requests.get(api_url).json()
        lh = r['lighthouseResult']['categories']
        return round(lh['seo']['score'] * 100, 1), round(lh['performance']['score'] * 100, 1)
    except: return "N/A", "N/A"

def generate_report(biz_name, url, city, seo, perf, gemini_key):
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")
    
    scrape_url = f"https://r.jina.ai/{url}"
    web_content = requests.get(scrape_url).text[:4000]
    
    prompt = f"""
    You are the Cognito AI Sales Copilot.
    Audit for: {biz_name} in {city}.
    URL: {url}
    Technical: SEO {seo}, Speed {perf}.
    Content: {web_content}

    FOCUS ON AI CHATBOT SALES. 
    NOTE: They have a manual WhatsApp button. Agitate the fact that manual replies cause lead drop-off.

    Provide the report in exactly these sections:
    [AI_READINESS]
    Score out of 100. List what's missing: AI Chatbot, 24/7 Automation, AI Lead Qualification.
    
    [COMPETITOR_SNAPSHOT]
    Identify 2 typical local competitors in {city} and compare their likely AI adoption vs this business.
    
    [OPPORTUNITIES]
    List 3 specific revenue-generating opportunities (e.g. AI Appointment Booking).
    
    [ROI_ESTIMATOR]
    A table showing manual handling vs AI automation costs and lead capture rates.

    [WHATSAPP_PITCH]
    A short, click-worthy message for the owner. Use the PAS framework. Mention their manual WhatsApp button vs an AI Agent.

    [EMAIL_PITCH]
    Subject lines + Body. High-end marketing psychology.
    """
    
    response = model.generate_content(prompt)
    return response.text

# 4. BEAUTIFUL PDF GENERATOR
class PDF(FPDF):
    def header(self):
        self.set_fill_color(0, 123, 255) # Blue Header
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 24)
        self.cell(0, 20, 'COGNITO AI SALES AUDIT', ln=True, align='C')
        self.ln(10)

def create_beautiful_pdf(report_text, biz_name):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    
    # Clean text
    clean_text = report_text.encode('latin-1', 'ignore').decode('latin-1')
    sections = clean_text.split("[")
    
    for section in sections:
        if not section.strip(): continue
        # Highlight Headers
        header_end = section.find("]")
        if header_end != -1:
            header_text = section[:header_end].replace("_", " ")
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(0, 123, 255)
            pdf.cell(0, 10, header_text.upper(), ln=True)
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 8, section[header_end+1:].strip())
            pdf.ln(5)
        else:
            pdf.multi_cell(0, 8, section.strip())
            
    return pdf.output()

# 5. UI EXECUTION
if st.button("🚀 Run Full Intelligence Audit"):
    if not (biz_name and target_url and gemini_key and google_key):
        st.error("Please fill in all profile details and API keys.")
    else:
        with st.spinner("Analyzing your prospect..."):
            seo, perf = get_tech_scores(target_url, google_key)
            full_report = generate_report(biz_name, target_url, city, seo, perf, gemini_key)
            
            # Parsing Sections
            def get_sec(tag):
                try: return full_report.split(f"[{tag}]")[1].split("[")[0].strip()
                except: return "Section not found."

            st.success(f"Audit Complete for {biz_name}")
            
            # --- DASHBOARD ---
            m1, m2, m3 = st.columns(3)
            m1.metric("SEO Score", f"{seo}%")
            m2.metric("Site Speed", f"{perf}%")
            m3.metric("Chatbot Status", "❌ Manual Only")

            t1, t2, t3, t4, t5 = st.tabs(["📊 Audit", "🏆 Competitors", "💰 ROI & Ops", "💬 WhatsApp Pitch", "✉️ Email Pitch"])
            
            with t1:
                st.markdown("### AI Readiness Score")
                st.markdown(get_sec("AI_READINESS"))
                # PDF BUTTON
                pdf_bytes = create_beautiful_pdf(full_report, biz_name)
                st.download_button("📩 Download Beautiful PDF Report", data=bytes(pdf_bytes), file_name=f"{biz_name}_Cognito_Audit.pdf", mime="application/pdf")

            with t2:
                st.markdown("### Competitor Snapshot")
                st.markdown(get_sec("COMPETITOR_SNAPSHOT"))

            with t3:
                st.markdown("### Opportunity & ROI")
                st.markdown(get_sec("OPPORTUNITIES"))
                st.divider()
                st.markdown(get_sec("ROI_ESTIMATOR"))

            with t4:
                st.subheader("WhatsApp Pitch (One-Click Copy)")
                st.code(get_sec("WHATSAPP_PITCH"), language="text")
                st.caption("Focuses on the 'Manual WhatsApp' time-drain.")

            with t5:
                st.subheader("Email Campaign")
                st.code(get_sec("EMAIL_PITCH"), language="text")
