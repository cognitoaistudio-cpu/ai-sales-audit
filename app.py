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
        return round(seo, 1), round(perf, 1)
    except:
        return 50, 50 # Default if Google API fails

def analyze_with_ai(url, seo, perf, gemini_key):
    try:
        genai.configure(api_key=gemini_key)
        
        # Try different model names in case one is restricted in your region
        model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        success = False
        for name in model_names:
            try:
                model = genai.GenerativeModel(name)
                
                # Get website text
                scrape_url = f"https://r.jina.ai/{url}"
                web_text = requests.get(scrape_url).text[:4000]
                
                prompt = f"""
                You are a Sales Intelligence Consultant. 
                Website Content: {web_text}
                SEO Score: {seo}/100, Performance: {perf}/100.
                
                Provide a professional audit. 
                Highlight if they are missing: AI Chatbots, WhatsApp, or Online Booking.
                Format clearly with bullet points.
                """
                
                response = model.generate_content(prompt)
                report_text = response.text
                success = True
                break # Stop if we found a working model
            except:
                continue
        
        if not success:
            return "Could not connect to AI. Check your API key at aistudio.google.com"
            
        return report_text
    except Exception as e:
        return f"General Error: {str(e)}"

# 4. THE USER INTERFACE
target_url = st.text_input("Enter Website URL (e.g., https://example.com)")

if st.button("Start Audit"):
    if not gemini_key or not google_key:
        st.error("Please add both API keys in the sidebar!")
    else:
        with st.spinner("Analyzing... this takes 20-30 seconds."):
            seo_score, perf_score = get_audit_data(target_url, google_key)
            report = analyze_with_ai(target_url, seo_score, perf_score, gemini_key)
            
            st.success("Audit Complete!")
            st.subheader(f"Results for {target_url}")
            st.write(f"**SEO:** {seo_score} | **Speed:** {perf_score}")
            st.markdown(report)
            
            # PDF Generation - Fixed for non-techie safety
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("helvetica", size=12)
                pdf.cell(200, 10, text=f"AI Audit: {target_url}", ln=True, align='C')
                pdf.ln(10)
                # Ensure text is compatible with PDF encoding
                clean_text = report.encode('latin-1', 'ignore').decode('latin-1')
                pdf.multi_cell(0, 10, text=clean_text)
                
                # Final PDF button logic
                pdf_bytes = pdf.output()
                st.download_button(
                    label="📩 Download PDF Report",
                    data=bytes(pdf_bytes),
                    file_name="Business_Audit.pdf",
                    mime="application/pdf"
                )
            except Exception as pdf_err:
                st.warning(f"Note: PDF generation had a small issue, but audit is visible above. Error: {pdf_err}")
