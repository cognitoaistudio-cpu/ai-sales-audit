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
    st.info("I will automatically find the best available AI model for your key.")

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
        genai.configure(api_key=gemini_key)
        
        # FIND THE BEST MODEL AUTOMATICALLY
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Preferred models in order of quality/speed
        preferred = ['models/gemini-3.5-flash', 'models/gemini-2.0-flash', 'models/gemini-1.5-flash', 'models/gemini-pro']
        
        best_model = None
        for p in preferred:
            if p in available_models:
                best_model = p
                break
        
        if not best_model:
            # If none of the preferred are found, just take the first one available
            best_model = available_models[0] if available_models else None

        if not best_model:
            return "TECHNICAL ERROR: No models available for this API key."

        st.write(f"⚙️ Using model: {best_model}")
        model = genai.GenerativeModel(best_model)
        
        # Scrape Content
        scrape_url = f"https://r.jina.ai/{url}"
        web_text = requests.get(scrape_url).text[:4000]
        
        prompt = f"""
        You are a Sales Intelligence Consultant. 
        Website: {url}
        Data: {web_text}
        SEO Score: {seo}/100, Performance: {perf}/100.
        
        Write a professional audit for this business. 
        Focus on:
        1. AI Readiness (Are they using chatbots/automation?)
        2. Customer Conversion Gaps (Speed, SEO, UX)
        3. A persuasive closing statement on how AI can increase their revenue.
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"TECHNICAL ERROR: {str(e)}"

# 4. THE USER INTERFACE
target_url = st.text_input("Enter Business Website (e.g., https://example.com)")

if st.button("Start Audit"):
    if not gemini_key or not google_key:
        st.error("Please provide both API keys in the sidebar.")
    else:
        with st.spinner("Running Audit..."):
            seo_score, perf_score = get_audit_data(target_url, google_key)
            report = analyze_with_ai(target_url, seo_score, perf_score, gemini_key)
            
            if "TECHNICAL ERROR" in report:
                st.error(report)
            else:
                st.success("Audit Complete!")
                st.write(f"**SEO Score:** {seo_score} | **Speed Score:** {perf_score}")
                st.markdown(report)
                
                # PDF Generation (Fixed for Streamlit download)
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", size=12)
                    # Clean text for PDF
                    clean_report = report.encode('latin-1', 'ignore').decode('latin-1')
                    pdf.multi_cell(0, 10, txt=f"Audit for {target_url}\n\n" + clean_report)
                    
                    # This converts the PDF to something the button can send
                    pdf_bytes = pdf.output()
                    st.download_button(
                        label="📩 Download PDF Report",
                        data=bytes(pdf_bytes),
                        file_name="Business_Audit.pdf",
                        mime="application/pdf"
                    )
                except Exception as pdf_error:
                    st.warning("Audit generated, but PDF failed. You can copy the text above.")
