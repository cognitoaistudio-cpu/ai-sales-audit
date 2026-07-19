import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF
import datetime

# 1. PAGE CONFIG
st.set_page_config(page_title="Cognito AI Copilot 3.0", layout="wide", page_icon="🤖")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; background-color: #ffffff; border-radius: 8px 8px 0 0;
        border: 1px solid #dfe3e6; padding: 10px 20px; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. PDF ENGINE (HIGH QUALITY 8-15 PAGE STRUCTURE)
class CognitoReport(FPDF):
    def __init__(self, biz_name, report_type="CLIENT"):
        super().__init__()
        self.biz_name = biz_name
        self.report_type = report_type
        self.date = datetime.date.today().strftime("%B %d, %Y")

    def cover_page(self):
        self.add_page()
        self.set_fill_color(30, 58, 138)
        self.rect(0, 0, 210, 297, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 28)
        self.ln(60)
        self.cell(0, 20, "DIGITAL GROWTH &", ln=True, align='C')
        self.cell(0, 20, "AI READINESS AUDIT", ln=True, align='C')
        self.ln(20)
        self.set_font('Arial', '', 18)
        self.cell(0, 10, f"Prepared for: {self.biz_name}", ln=True, align='C')
        self.ln(80)
        self.set_font('Arial', 'I', 12)
        self.cell(0, 10, f"Audit Date: {self.date}", ln=True, align='C')
        self.cell(0, 10, "Prepared by: Cognito AI Studio", ln=True, align='C')

    def header(self):
        if self.page_no() > 1:
            self.set_text_color(100, 100, 100)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f"Cognito AI Studio | Digital Audit: {self.biz_name}", 0, 0, 'R')
            self.ln(10)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_section(self, title, content):
        self.add_page()
        self.set_text_color(30, 58, 138)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, title.upper(), ln=True)
        self.ln(5)
        self.set_text_color(50, 50, 50)
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 7, safe_text(content))

def safe_text(text):
    return text.encode('ascii', 'ignore').decode('ascii')

# 3. CORE ANALYTICS
def get_scores(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=SEO&category=PERFORMANCE&key={api_key}"
    try:
        r = requests.get(api_url).json()
        lh = r['lighthouseResult']['categories']
        return round(lh['seo']['score']*100), round(lh['performance']['score']*100)
    except: return 50, 45

def run_ai_logic(biz_data, tech_scores, gemini_key):
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")
    
    scrape_url = f"https://r.jina.ai/{biz_data['url']}"
    web_text = requests.get(scrape_url).text[:4000]
    
    prompt = f"""
    You are the Cognito AI Sales Strategist. Audit for {biz_data['name']} in {biz_data['city']}.
    SEO: {tech_scores[0]}, Website Health: {tech_scores[1]}. 
    Context: {web_text}

    Generate 3 data blocks. Use markers [SCORECARD], [CLIENT_REPORT], [INTERNAL_STRATEGY], [OUTREACH].

    [SCORECARD]
    Provide scores out of 100 for: Website, SEO, Google Business, Social Media, Customer Experience, Lead Capture, AI Readiness, Online Reputation.
    Format: Category|Score|Status(🟢,🟡,🔴)

    [CLIENT_REPORT]
    Break into these exact sections:
    1. Executive Summary (Digital Health Overview)
    2. Top 5 Strengths & Top 5 Opportunities
    3. Website Audit Details (Navigation, CTAs, Trust Signals)
    4. Google Business Profile & Social Media Status
    5. Customer Journey Analysis (Friction points from search to booking)
    6. AI Readiness Table (Feature|Status: YES/NO)
    7. Priority Recommendations (Priority|Action|Impact)

    [INTERNAL_STRATEGY]
    1. Lead Qualification (High/Med/Low)
    2. Technical Debt & SEO Details
    3. Competitor Intel (2 local rivals)
    4. Objection Handling (Prepare for 'We don't need AI')
    5. Proposal Builder (Phase 1-3)

    [OUTREACH]
    WhatsApp Pitch & Email Sequence.
    """
    return model.generate_content(prompt).text

# 4. APP UI
st.title("🤖 Cognito AI Sales Copilot")

with st.sidebar:
    st.header("🏢 Target Business")
    b_name = st.text_input("Business Name")
    b_url = st.text_input("Website (https://...)")
    b_city = st.text_input("City")
    st.divider()
    g_key = st.text_input("Gemini API Key", type="password")
    ps_key = st.text_input("PageSpeed API Key", type="password")

if st.button("🚀 Run Full Cognito Audit"):
    if not (b_name and b_url and g_key):
        st.error("Please fill all details.")
    else:
        with st.spinner("Analyzing Digital Footprint..."):
            seo, health = get_scores(b_url, ps_key)
            full_data = run_ai_logic({"name": b_name, "url": b_url, "city": b_city}, (seo, health), g_key)
            
            def parse(tag):
                try: return full_data.split(f"[{tag}]")[1].split("[")[0].strip()
                except: return "Section failed."

            scorecard_raw = parse("SCORECARD")
            client_raw = parse("CLIENT_REPORT")
            internal_raw = parse("INTERNAL_STRATEGY")
            outreach_raw = parse("OUTREACH")

            st.success("Audit Complete.")

            t1, t2, t3 = st.tabs(["📄 Client Report™", "🔐 Internal Strategy", "✉️ Outreach"])

            with t1:
                st.markdown(f"### Digital Scorecard for {b_name}")
                st.text(scorecard_raw)
                st.markdown("---")
                st.markdown(client_raw)
                
                # PDF BUILDER
                pdf = CognitoReport(b_name)
                pdf.cover_page()
                pdf.add_section("Digital Scorecard", scorecard_raw)
                # Split client_raw into sections for multiple pages
                sections = client_raw.split("\n\n")
                for sec in sections:
                    if len(sec) > 20: pdf.add_section("Audit Detail", sec)
                
                st.download_button("📩 Download 8-15 Page Client Audit", bytes(pdf.output()), f"{b_name}_Cognito_Audit.pdf", "application/pdf")

            with t2:
                st.warning("INTERNAL USE ONLY")
                st.markdown(internal_raw)
                
                pdf_i = CognitoReport(b_name, "INTERNAL")
                pdf_i.add_page()
                pdf_i.set_font("Arial", size=10)
                pdf_i.multi_cell(0, 10, safe_text(internal_raw))
                st.download_button("🕵️ Download Internal Intel", bytes(pdf_i.output()), f"{b_name}_INTERNAL.pdf")

            with t3:
                st.code(outreach_raw)
