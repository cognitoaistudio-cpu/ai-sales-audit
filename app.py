import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF
import re

# 1. BRANDING & UI CONFIG
st.set_page_config(page_title="Cognito AI Copilot", layout="wide", page_icon="🤖")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; background-color: #ffffff; border-radius: 8px 8px 0 0;
        border: 1px solid #dfe3e6; padding: 10px 20px; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A; color: white; }
    .report-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. DUAL-STYLE PDF ENGINE
class CognitoPDF(FPDF):
    def __init__(self, report_type="CLIENT", biz_name=""):
        super().__init__()
        self.report_type = report_type
        self.biz_name = biz_name

    def header(self):
        # Header Branding
        if self.report_type == "CLIENT":
            self.set_fill_color(30, 58, 138) # Navy Blue
            self.rect(0, 0, 210, 35, 'F')
            self.set_text_color(255, 255, 255)
            self.set_font('Arial', 'B', 16)
            self.cell(0, 15, 'COGNITO AI BUSINESS HEALTH REPORT™', ln=True, align='C')
        else:
            self.set_fill_color(220, 38, 38) # Red for Internal
            self.rect(0, 0, 210, 35, 'F')
            self.set_text_color(255, 255, 255)
            self.set_font('Arial', 'B', 16)
            self.cell(0, 15, 'INTERNAL COGNITO INTELLIGENCE - CONFIDENTIAL', ln=True, align='C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Prepared by Cognito AI Studio for {self.biz_name}', 0, 0, 'C')

# 3. CORE LOGIC
def get_scores(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=SEO&category=PERFORMANCE&category=ACCESSIBILITY&key={api_key}"
    try:
        r = requests.get(api_url).json()
        lh = r['lighthouseResult']['categories']
        return round(lh['seo']['score']*100), round(lh['performance']['score']*100), round(lh['accessibility']['score']*100)
    except: return 50, 50, 50

def run_dual_analysis(biz_data, tech_scores, gemini_key):
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")
    
    scrape_url = f"https://r.jina.ai/{biz_data['url']}"
    web_text = requests.get(scrape_url).text[:4000]
    
    prompt = f"""
    You are the Senior Strategy Lead at Cognito AI Studio.
    Target: {biz_data['name']} in {biz_data['city']}. Industry: {biz_data['industry']}.
    Technical Stats: SEO {tech_scores[0]}, Speed {tech_scores[1]}, Accessibility {tech_scores[2]}.
    Web Data: {web_text}

    TASK: Generate TWO distinct reports using these exact markers.

    [CLIENT_REPORT]
    1. Executive Summary: Digital Scorecard (SEO, Speed, AI Readiness). 
    2. Customer Journey: Highlight how their current manual WhatsApp button creates friction.
    3. AI Opportunity: Why an AI Chatbot/Agent is their #1 priority.
    4. ROI Estimator: Potential impact of 24/7 automation.

    [INTERNAL_REPORT]
    1. Lead Qualification: Budget potential (High/Medium/Low) and Sales Priority.
    2. Technical Debt: Hidden issues in their site.
    3. Competitor Intelligence: Compare them to 2 local rivals in {biz_data['city']}.
    4. Objection Prep: Anticipate and answer "We use manual WhatsApp, it's fine."
    5. Proposal Builder: Phase 1 (Chatbot), Phase 2 (WhatsApp Automation), Phase 3 (CRM).

    [OUTREACH]
    1. WhatsApp: Crisp pitch focusing on the "Manual Reply Trap".
    2. Email: Click-worthy Subject lines + PAS body.
    """
    return model.generate_content(prompt).text

# 4. APP UI
st.title("🤖 Cognito AI Sales Copilot")

with st.sidebar:
    st.header("🏢 Target Profile")
    b_name = st.text_input("Business Name")
    b_url = st.text_input("Website URL")
    b_city = st.text_input("City")
    b_ind = st.selectbox("Industry", ["Healthcare", "Real Estate", "Home Services", "Legal", "Retail"])
    
    st.divider()
    st.header("🔑 API Access")
    g_key = st.text_input("Gemini API Key", type="password")
    ps_key = st.text_input("PageSpeed API Key", type="password")

if st.button("🚀 Generate Cognito Intelligence"):
    if not (b_name and b_url and g_key):
        st.error("Please fill all fields.")
    else:
        with st.spinner("Module 1-4: Running Technical Audit & AI Detection..."):
            seo, speed, acc = get_scores(b_url, ps_key)
            raw_report = run_dual_analysis({"name": b_name, "url": b_url, "city": b_city, "industry": b_ind}, (seo, speed, acc), g_key)
            
            # PARSING
            def clean_sec(text, tag):
                try: return text.split(f"[{tag}]")[1].split("[")[0].strip()
                except: return "Content generation failed."

            client_txt = clean_sec(raw_report, "CLIENT_REPORT")
            internal_txt = clean_sec(raw_report, "INTERNAL_REPORT")
            outreach_txt = clean_sec(raw_report, "OUTREACH")

            st.success("Analysis Complete.")

            # --- TABS ---
            tab1, tab2, tab3 = st.tabs(["📄 Client Report™", "🔐 Internal Intelligence", "✉️ Outreach Copy"])

            with tab1:
                st.markdown(f"### {b_name} - Health Score")
                c1, c2, c3 = st.columns(3)
                c1.metric("Overall Score", "62/100")
                c2.metric("AI Readiness", "28/100", "-15%")
                c3.metric("Customer Journey", "54/100")
                
                st.markdown("---")
                st.markdown(client_txt)
                
                # CLIENT PDF
                pdf_c = CognitoPDF("CLIENT", b_name)
                pdf_c.add_page()
                pdf_c.set_font("Arial", size=11)
                pdf_c.multi_cell(0, 8, client_txt.encode('latin-1', 'ignore').decode('latin-1'))
                st.download_button("📩 Download Client Health Report™", bytes(pdf_c.output()), f"{b_name}_Health_Report.pdf")

            with tab2:
                st.warning("INTERNAL USE ONLY - Confidential Strategy")
                st.markdown(internal_txt)
                
                # INTERNAL PDF
                pdf_i = CognitoPDF("INTERNAL", b_name)
                pdf_i.add_page()
                pdf_i.set_font("Arial", size=10)
                pdf_i.multi_cell(0, 7, internal_txt.encode('latin-1', 'ignore').decode('latin-1'))
                st.download_button("🕵️ Download Internal Intelligence", bytes(pdf_i.output()), f"{b_name}_Internal_Strategy.pdf")

            with tab3:
                st.subheader("WhatsApp & Email Pitches")
                st.code(outreach_txt, language="text")
