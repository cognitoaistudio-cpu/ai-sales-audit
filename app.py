import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF

# 1. SETUP PAGE
st.set_page_config(page_title="AI Sales Auditor", layout="wide")
st.title("🚀 AI Business Audit & Sales Copilot")
st.subheader("Enter a business website to generate a professional AI audit.")

# 2. SIDEBAR - SECRETS (Where you put your keys)
with st.sidebar:
    st.header("Settings")
    st.info("Get keys from Google AI Studio and PageSpeed Insights API")
    gemini_key = st.text_input("Enter Gemini API Key", type="password")
    google_key = st.text_input("Enter PageSpeed API Key", type="password")

# 3. CORE FUNCTIONS
def get_audit_data(url, api_key):
    # This checks Google for SEO and Speed
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=SEO&category=PERFORMANCE&key={api_key}"
    try:
        r = requests.get(api_url).json()
        seo = r['lighthouseResult']['categories']['seo']['score'] * 100
        perf = r['lighthouseResult']['categories']['performance']['score'] * 100
        return seo, perf
    except:
        return "N/A", "N/A"

def analyze_with_ai(url, seo, perf, gemini_key):
    # This asks the AI to read the website
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Use Jina Reader to "see" the site
    scrape_url = f"https://r.jina.ai/{url}"
    try:
        web_text = requests.get(scrape_url).text[:5000] # Get first 5000 characters
    except:
        web_text = "Could not retrieve website text."
    
    prompt = f"""
    You are a professional Sales Intelligence Consultant. 
    Analyze this website data: {web_text}
    SEO Score: {seo}/100, Performance Score: {perf}/100.
    
    Create a report with:
    1. A 'Digital Health' summary.
    2. Missing AI features (Chatbots, Booking, WhatsApp).
    3. Three specific recommendations to increase revenue.
    Be professional and persuasive.
    """
    response = model.generate_content(prompt)
    return response.text

# 4. THE USER INTERFACE
target_url = st.text_input("Business Website URL (e.g., https://example.com)")

if st.button("Start Audit"):
    if not gemini_key or not google_key:
        st.error("Please add your API keys in the sidebar first!")
    else:
        with st.spinner("Analyzing site... this takes about 30 seconds."):
            seo, perf = get_audit_data(target_url, google_key)
            report = analyze_with_ai(target_url, seo, perf, gemini_key)
            
            st.success("Audit Complete!")
            st.markdown("### 📊 Business Insights")
            st.write(f"**SEO Score:** {seo} | **Speed Score:** {perf}")
            st.markdown(report)
            
            # PDF Generation logic
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                # Clean text for PDF compatibility
                clean_text = report.encode('latin-1', 'ignore').decode('latin-1')
                pdf.multi_cell(0, 10, txt=f"Audit for: {target_url}\n\n" + clean_text)
                pdf_output = "audit_report.pdf"
                pdf.output(pdf_output)
                
                with open(pdf_output, "rb") as f:
                    st.download_button("📩 Download PDF Report", f, file_name="Business_Audit.pdf")
            except Exception as e:
                st.error(f"PDF Error: {e}")
