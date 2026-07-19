import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF

# 1. SETUP PAGE
st.set_page_config(page_title="AI Sales Intelligence", layout="wide")
st.title("🚀 AI Sales Intelligence & Outreach")

# 2. SIDEBAR
with st.sidebar:
    st.header("Settings")
    gemini_key = st.text_input("Enter Gemini API Key", type="password")
    google_key = st.text_input("Enter PageSpeed API Key", type="password")
    st.divider()
    st.info("Tip: If you get a 'Quota Error', wait 60 seconds and try again.")

# 3. CORE FUNCTIONS
def get_audit_data(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=SEO&category=PERFORMANCE&key={api_key}"
    try:
        r = requests.get(api_url).json()
        seo = r['lighthouseResult']['categories']['seo']['score'] * 100
        perf = r['lighthouseResult']['categories']['performance']['score'] * 100
        return round(seo, 1), round(perf, 1)
    except:
        return "N/A", "N/A"

def analyze_and_write(url, seo, perf, gemini_key):
    try:
        genai.configure(api_key=gemini_key)
        
        # PRIORITIZE 1.5 FLASH for higher free-tier limits
        # We try 1.5 Flash first, then 1.5 Pro, then whatever is available
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        scrape_url = f"https://r.jina.ai/{url}"
        # We limit text to 3000 characters to save "Tokens" (this prevents 429 errors)
        web_text = requests.get(scrape_url).text[:3000]
        
        prompt = f"""
        Act as a Sales Marketer. Website: {url}. Data: SEO {seo}, Speed {perf}. 
        Web Context: {web_text}
        
        Provide:
        ---REPORT---
        Audit the site for missing AI/automation.
        ---WHATSAPP---
        Short, crisp pitch with emojis.
        ---EMAIL---
        Subject: Found a gap in {url}
        Body: PAS framework pitch.
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        if "429" in str(e):
            return "TECHNICAL ERROR: Google's free limit reached. Please wait 1 minute and click the button again."
        return f"TECHNICAL ERROR: {str(e)}"

# 4. THE USER INTERFACE
target_url = st.text_input("Enter Business Website (e.g., https://example.com)")

if st.button("Generate Audit & Outreach"):
    if not gemini_key or not google_key:
        st.error("Please add keys in the sidebar.")
    else:
        with st.spinner("Analyzing... (Google Free Tier may take a moment)"):
            seo_score, perf_score = get_audit_data(target_url, google_key)
            full_response = analyze_and_write(target_url, seo_score, perf_score, gemini_key)
            
            if "TECHNICAL ERROR" in full_response:
                st.error(full_response)
            else:
                # SPLITTING LOGIC
                try:
                    parts = full_response.split("---")
                    # We look for keywords to ensure we get the right sections
                    audit_content = ""
                    whatsapp_content = ""
                    email_content = ""
                    for part in parts:
                        if "REPORT" in part: audit_content = part.replace("REPORT", "").strip()
                        if "WHATSAPP" in part: whatsapp_content = part.replace("WHATSAPP", "").strip()
                        if "EMAIL" in part: email_content = part.replace("EMAIL", "").strip()
                except:
                    audit_content = full_response
                    whatsapp_content = "Please retry for messaging."
                    email_content = "Please retry for messaging."

                st.success("Success!")
                tab1, tab2, tab3 = st.tabs(["📊 Audit Report", "💬 WhatsApp", "✉️ Email"])
                
                with tab1:
                    st.write(f"**SEO:** {seo_score} | **Speed:** {perf_score}")
                    st.markdown(audit_content)
                    try:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Helvetica", size=12)
                        clean_report = audit_content.encode('latin-1', 'ignore').decode('latin-1')
                        pdf.multi_cell(0, 10, txt=clean_report)
                        st.download_button("Download PDF", bytes(pdf.output()), "Audit.pdf", "application/pdf")
                    except: st.write("Download unavailable, copy text above.")

                with tab2:
                    st.code(whatsapp_content, language="text")

                with tab3:
                    st.code(email_content, language="text")
