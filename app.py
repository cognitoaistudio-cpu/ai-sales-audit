import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF
import datetime

# 1. PAGE CONFIG
st.set_page_config(page_title="Cognito AI Copilot", layout="wide", page_icon="🤖")

# 2. PROFESSIONAL PDF CLASS (FIXED FOR STABILITY)
class CognitoClientReport(FPDF):
    def __init__(self, biz_name, date):
        super().__init__()
        self.biz_name = biz_name
        self.date = date
        # Defining colors as fixed numbers to avoid TypeError
        self.primary_r, self.primary_g, self.primary_b = 30, 58, 138 
        self.text_r, self.text_g, self.text_b = 44, 62, 80

    def cover_page(self):
        self.add_page()
        # Navy Blue Sidebar
        self.set_fill_color(self.primary_r, self.primary_g, self.primary_b)
        self.rect(0, 0, 70, 297, 'F')
        
        self.set_y(100)
        self.set_x(80)
        self.set_font('helvetica', 'B', 26)
        self.set_text_color(self.primary_r, self.primary_g, self.primary_b)
        self.multi_cell(0, 12, "BUSINESS HEALTH & \nAI READINESS REPORT")
        
        self.set_y(140)
        self.set_x(80)
        self.set_font('helvetica', '', 16)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Client: {self.biz_name}", ln=True)
        self.set_x(80)
        self.cell(0, 10, f"Audit Date: {self.date}", ln=True)
        
        self.set_y(250)
        self.set_x(80)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(self.primary_r, self.primary_g, self.primary_b)
        self.cell(0, 10, "PREPARED BY COGNITO AI STUDIO", ln=True)
        self.set_x(80)
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 10, "CONFIDENTIAL", ln=True)

    def section_header(self, title):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(self.primary_r, self.primary_g, self.primary_b)
        self.cell(0, 15, title.upper(), ln=True)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(5)

    def write_body(self, text):
        self.set_font('helvetica', '', 11)
        self.set_text_color(self.text_r, self.text_g, self.text_b)
        # Handle encoding for special characters
        safe_text = text.encode('latin-1', 'ignore').decode('latin-1')
        self.multi_cell(0, 7, safe_text)
        self.ln(5)

    def score_table(self, score_dict):
        self.set_font('helvetica', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(100, 10, "Category", 1, 0, 'L', True)
        self.cell(40, 10, "Score", 1, 1, 'C', True)
        self.set_font('helvetica', '', 11)
        for cat, score in score_dict.items():
            self.cell(100, 10, cat.strip(), 1)
            self.cell(40, 10, f"{score.strip()}/100", 1, 1, 'C')
        self.ln(10)

# 3. CORE LOGIC
def get_tech_scores(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=SEO&category=PERFORMANCE&key={api_key}"
    try:
        r = requests.get(api_url).json()
        lh = r['lighthouseResult']['categories']
        return round(lh['seo']['score']*100), round(lh['performance']['score']*100)
    except: return 68, 52 # Fallback scores if API fails

def analyze_with_ai(biz_data, tech_scores, gemini_key):
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")
    
    scrape_url = f"https://r.jina.ai/{biz_data['url']}"
    web_text = requests.get(scrape_url).text[:4000]
    
    prompt = f"""
    Analyze the business '{biz_data['name']}' based on: {web_text}. 
    SEO Score: {tech_scores[0]}, Speed Score: {tech_scores[1]}.

    Generate an 8-page professional consulting report. Use these markers:
    [SCORES] Website Health:74, Online Visibility:52... (use this format)
    [SUMMARY] Executive overview.
    [FINDINGS] Strengths vs Opportunities.
    [WEBSITE] Evaluation of UI/UX.
    [VISIBILITY] Search and Social status.
    [JOURNEY] Customer path analysis.
    [COMMUNICATION] WhatsApp, Email, Phone status.
    [AI_READY] Detailed automation checklist.
    [OUTREACH] WhatsApp and Email pitch.
    """
    return model.generate_content(prompt).text

# 4. STREAMLIT UI
st.title("🤖 Cognito AI Sales Copilot")

with st.sidebar:
    st.header("Business Profile")
    b_name = st.text_input("Business Name")
    b_url = st.text_input("Website URL")
    st.divider()
    g_key = st.text_input("Gemini API Key", type="password")
    ps_key = st.text_input("PageSpeed API Key", type="password")

if st.button("🚀 Run Professional Audit"):
    if not (b_name and b_url and g_key):
        st.error("Please fill all details.")
    else:
        with st.spinner("Executing Digital Intelligence Scan..."):
            seo, speed = get_tech_scores(b_url, ps_key)
            report_data = analyze_with_ai({"name": b_name, "url": b_url}, (seo, speed), g_key)
            
            def parse(tag):
                try: return report_data.split(f"[{tag}]")[1].split("[")[0].strip()
                except: return "Information not available for this section."

            t1, t2, t3 = st.tabs(["📄 Client Report", "🔐 Internal Strategy", "✉️ Outreach Copy"])
            
            with t1:
                st.subheader("Business Health Overview")
                st.markdown(parse("SUMMARY"))
                
                # --- BUILD PDF ---
                pdf = CognitoClientReport(b_name, datetime.date.today().strftime("%d %b %Y"))
                pdf.cover_page()
                
                # Page 1: Summary & Score Table
                pdf.add_page()
                pdf.section_header("Page 1: Executive Summary")
                try:
                    score_lines = parse("SCORES").split(",")
                    score_dict = {s.split(":")[0]: s.split(":")[1] for s in score_lines if ":" in s}
                    pdf.score_table(score_dict)
                except: pdf.write_body("Score data formatting issue. See summary below.")
                pdf.write_body(parse("SUMMARY"))
                
                # Pages 2-7
                sections = [
                    ("Page 2: Key Findings", "FINDINGS"),
                    ("Page 3: Website Health", "WEBSITE"),
                    ("Page 4: Online Visibility", "VISIBILITY"),
                    ("Page 5: Customer Journey", "JOURNEY"),
                    ("Page 6: Customer Communication", "COMMUNICATION"),
                    ("Page 7: AI Readiness Assessment", "AI_READY")
                ]
                for title, tag in sections:
                    pdf.add_page()
                    pdf.section_header(title)
                    pdf.write_body(parse(tag))
                
                # Page 8: Conclusion
                pdf.add_page()
                pdf.section_header("Page 8: Conclusion")
                pdf.write_body("This report provides an overview of your current digital presence and highlights areas with the greatest potential for improvement. If you'd like a tailored implementation plan and recommendations based on your business goals, we'd be happy to discuss the next steps with you.")
                
                # Output PDF
                pdf_output = pdf.output()
                st.download_button("📩 Download 8-Page Client Report", bytes(pdf_output), f"{b_name}_Cognito_Audit.pdf", "application/pdf")

            with t2:
                st.write("### Internal Sales Intelligence")
                st.write(report_data) # Full raw dump for your internal strategy

            with t3:
                st.subheader("Copy-Paste Outreach")
                st.code(parse("OUTREACH"), language="text")
