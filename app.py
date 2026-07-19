import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF
import datetime

# 1. PAGE CONFIG
st.set_page_config(page_title="Cognito AI Copilot", layout="wide", page_icon="🤖")

# 2. PROFESSIONAL PDF CLASS
class CognitoClientReport(FPDF):
    def __init__(self, biz_name, date):
        super().__init__()
        self.biz_name = biz_name
        self.date = date
        self.primary_color = (30, 58, 138) # Professional Navy Blue
        self.text_color = (44, 62, 80)
        self.grey = (127, 140, 141)

    def cover_page(self):
        self.add_page()
        # Navy Blue Sidebar
        self.set_fill_color(*self.primary_color)
        self.rect(0, 0, 70, 297, 'F')
        
        self.set_y(100)
        self.set_x(80)
        self.set_font('helvetica', 'B', 26)
        self.set_text_color(*self.primary_color)
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
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, "PREPARED BY COGNITO AI STUDIO", ln=True)
        self.set_x(80)
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 10, "CONFIDENTIAL", ln=True)

    def section_header(self, title):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(*self.primary_color)
        self.cell(0, 15, title.upper(), ln=True)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(5)

    def write_body(self, text):
        self.set_font('helvetica', '', 11)
        self.set_text_color(*self.text_color)
        self.multi_cell(0, 7, text.encode('latin-1', 'ignore').decode('latin-1'))
        self.ln(5)

    def score_table(self, scores):
        self.set_font('helvetica', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(100, 10, "Category", 1, 0, 'L', True)
        self.cell(40, 10, "Score", 1, 1, 'C', True)
        self.set_font('helvetica', '', 11)
        for cat, score in scores.items():
            self.cell(100, 10, cat, 1)
            self.cell(40, 10, f"{score}/100", 1, 1, 'C')
        self.ln(10)

# 3. CORE LOGIC
def get_tech_scores(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=SEO&category=PERFORMANCE&key={api_key}"
    try:
        r = requests.get(api_url).json()
        lh = r['lighthouseResult']['categories']
        return round(lh['seo']['score']*100), round(lh['performance']['score']*100)
    except: return 65, 55

def analyze_with_ai(biz_data, tech_scores, gemini_key):
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")
    
    scrape_url = f"https://r.jina.ai/{biz_data['url']}"
    web_text = requests.get(scrape_url).text[:4000]
    
    prompt = f"""
    You are a Senior Strategic Consultant. Generate a 8-page report for {biz_data['name']}.
    Data: SEO {tech_scores[0]}, Performance {tech_scores[1]}. Context: {web_text}
    
    Return the content using these markers exactly:
    [SCORES] Category:Score pairs
    [SUMMARY] (150-250 words)
    [FINDINGS] Strengths and Opportunities
    [WEBSITE] Evaluation of design, speed, and CTAs
    [VISIBILITY] Google Business, Social Media, Reviews
    [JOURNEY] 5-step journey analysis
    [COMMUNICATION] Phone, WhatsApp, Chat evaluation
    [AI_READY] Status of AI Automation features
    [OUTREACH] WhatsApp and Email copy
    """
    return model.generate_content(prompt).text

# 4. STREAMLIT UI
st.title("🤖 Cognito AI Sales Intelligence")

with st.sidebar:
    st.header("Business Profile")
    b_name = st.text_input("Business Name")
    b_url = st.text_input("Website URL")
    st.divider()
    g_key = st.text_input("Gemini API Key", type="password")
    ps_key = st.text_input("PageSpeed API Key", type="password")

if st.button("🚀 Generate Professional Intelligence"):
    if not (b_name and b_url and g_key):
        st.error("Please fill all details.")
    else:
        with st.spinner("Analyzing Digital Presence..."):
            seo, speed = get_tech_scores(b_url, ps_key)
            report_data = analyze_with_ai({"name": b_name, "url": b_url}, (seo, speed), g_key)
            
            def parse(tag):
                try: return report_data.split(f"[{tag}]")[1].split("[")[0].strip()
                except: return "Data currently unavailable for this section."

            # Tab Display
            t1, t2, t3 = st.tabs(["📄 Client Report", "🔐 Internal Strategy", "✉️ Outreach Copy"])
            
            with t1:
                st.success("Report Generated Successfully")
                st.markdown(parse("SUMMARY"))
                
                # PDF BUILDING
                pdf = CognitoClientReport(b_name, datetime.date.today().strftime("%d %b %Y"))
                pdf.cover_page()
                
                # Page 1: Summary
                pdf.add_page()
                pdf.section_header("Page 1: Executive Summary")
                # Parsing Scores for table
                score_lines = parse("SCORES").split("\n")
                score_dict = {line.split(":")[0]: line.split(":")[1] for line in score_lines if ":" in line}
                pdf.score_table(score_dict)
                pdf.write_body(parse("SUMMARY"))
                
                # Page 2: Findings
                pdf.add_page()
                pdf.section_header("Page 2: Key Findings")
                pdf.write_body(parse("FINDINGS"))
                
                # Page 3: Website
                pdf.add_page()
                pdf.section_header("Page 3: Website Health")
                pdf.write_body(parse("WEBSITE"))
                
                # Page 4: Visibility
                pdf.add_page()
                pdf.section_header("Page 4: Online Visibility")
                pdf.write_body(parse("VISIBILITY"))
                
                # Page 5: Journey
                pdf.add_page()
                pdf.section_header("Page 5: Customer Journey")
                pdf.write_body(parse("JOURNEY"))
                
                # Page 6: Communication
                pdf.add_page()
                pdf.section_header("Page 6: Customer Communication")
                pdf.write_body(parse("COMMUNICATION"))
                
                # Page 7: AI Readiness
                pdf.add_page()
                pdf.section_header("Page 7: AI Readiness Assessment")
                pdf.write_body(parse("AI_READY"))
                
                # Page 8: Conclusion
                pdf.add_page()
                pdf.section_header("Page 8: Conclusion")
                pdf.write_body("This report provides an overview of your current digital presence and highlights areas with the greatest potential for improvement. If you'd like a tailored implementation plan and recommendations based on your business goals, we'd be happy to discuss the next steps with you.")
                
                st.download_button("📩 Download 8-Page Client Report", bytes(pdf.output()), f"{b_name}_Cognito_Audit.pdf", "application/pdf")

            with t2:
                st.info("INTERNAL COGNITO STRATEGY")
                st.markdown("Use this to prepare for your sales call.")
                st.write(report_data) # Internal detailed view

            with t3:
                st.subheader("Outreach Tools")
                st.code(parse("OUTREACH"), language="text")
