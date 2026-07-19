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
    st.info("Get your Gemini Key at: https://aistudio.google.com/")
    gemini_key = st.text_input("Enter Gemini API Key", type="password")
    google_key = st.text_input("Enter PageSpeed API Key", type="password")

# 3. CORE FUNCTIONS
def get_audit_data(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=SEO&category=PERFORMANCE&key={api_key}"
    try:
        r = requests.get(api_url).json()
        seo = r['lighthouseResult']['categories']['seo']['score'] * 100
        perf = r['lighthouseResult']['categories']['performance']['score'] * 100
        return seo, perf
    except:
        return "N/A", "N/A"

def analyze_with_ai(url, seo, perf, gemini_key):
    try:
        genai.configure(api_key=gemini_key)
        
        # FIX: We try the most common model names in order
        model_to_use = 'gemini-1.5-flash' 
        model = genai.GenerativeModel(model_to_use)
        
        scrape_url = f"https://r.jina.ai/{url}"
        web_text = requests.get(scrape_url).text[:5000]
        
        prompt = f"""
        You are a Sales Consultant. Analyze this website: {url}
        Content: {web_text}
        SEO: {seo}, Speed: {perf}
        Write a brief audit report identifying missing AI tools like chatbots or booking systems.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}. Please check if your Gemini API key is correct and active."

# 4. THE USER INTERFACE
target_url = st.text_input("Business Website URL (e.g., https://example.com)")

if st.button("Start Audit"):
    if not gemini_key or not google_key:
        st.error("Please add both API keys in the sidebar!")
    else:
        with st.spinner("Analyzing... please wait..."):
            seo, perf = get_audit_data(target_url, google_key)
            report = analyze_with_ai(target_url, seo, perf, gemini_key)
            
            st.success("Audit Complete!")
            st.markdown(report)
            
            # Simple PDF setup
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, txt=f"Audit for: {target_url}\n\n" + report.encode('latin-1', 'ignore').decode('latin-1'))
            
            st.download_button("📩 Download PDF Report", pdf.output(dest='S'), file_name="Audit.pdf")
