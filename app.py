import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF

# 1. SETUP PAGE
st.set_page_config(page_title="AI Sales Auditor", layout="wide")
st.title("🚀 AI Business Audit & Sales Copilot")

# 2. SIDEBAR
with st.sidebar:
    st.header("Settings")
    gemini_key = st.text_input("Enter Gemini API Key", type="password")
    google_key = st.text_input("Enter PageSpeed API Key", type="password")
    st.divider()
    st.write("Need a key? [Get it here](https://aistudio.google.com/app/apikey)")

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

def analyze_with_ai(url, seo, perf, gemini_key):
    try:
        # Step 1: Initialize
        genai.configure(api_key=gemini_key)
        
        # Step 2: Set the model (using the full path)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        # Step 3: Get Website Content
        scrape_url = f"https://r.jina.ai/{url}"
        try:
            web_text = requests.get(scrape_url, timeout=10).text[:4000]
        except:
            web_text = "Could not crawl website text."

        # Step 4: Ask AI
        prompt = f"Analyze this website for a sales pitch: {url}. Data: {web_text}. SEO: {seo}. Identify missing AI features."
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        # This will show us the REAL error
        return f"TECHNICAL ERROR: {str(e)}"

# 4. THE USER INTERFACE
target_url = st.text_input("Enter Website URL (e.g., https://example.com)")

if st.button("Start Audit"):
    if not gemini_key or not google_key:
        st.error("Missing API keys in the sidebar.")
    else:
        with st.spinner("Talking to AI..."):
            seo_score, perf_score = get_audit_data(target_url, google_key)
            report = analyze_with_ai(target_url, seo_score, perf_score, gemini_key)
            
            if "TECHNICAL ERROR" in report:
                st.error(report)
                st.info("Check if your API Key has 'Generative AI API' enabled in Google Cloud.")
            else:
                st.success("Audit Complete!")
                st.markdown(report)
                
                # PDF Logic
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("helvetica", size=12)
                    pdf.multi_cell(0, 10, text=report.encode('latin-1', 'ignore').decode('latin-1'))
                    st.download_button("Download PDF", pdf.output(), "Audit.pdf", "application/pdf")
                except:
                    st.write("PDF failed, but audit is above.")
