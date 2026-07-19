import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF

# 1. SETUP PAGE
st.set_page_config(page_title="AI Sales Intelligence 3.0", layout="wide")
st.title("🚀 AI Sales Intelligence & Outreach")

# 2. SIDEBAR
with st.sidebar:
    st.header("Settings")
    gemini_key = st.text_input("Enter Gemini API Key", type="password").strip()
    google_key = st.text_input("Enter PageSpeed API Key", type="password").strip()
    st.divider()
    st.info("Using Advanced Parsing to ensure your report generates every time.")

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
        
        # Find Model
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preferred = ['models/gemini-3-flash-preview', 'models/gemini-1.5-flash', 'models/gemini-2.0-flash']
        best_model = next((p for p in preferred if p in available_models), available_models[0])
        
        model = genai.GenerativeModel(best_model)
        
        # Get Website Context
        scrape_url = f"https://r.jina.ai/{url}"
        web_text = requests.get(scrape_url).text[:4000]
        
        # STRENGTHENED PROMPT
        prompt = f"""
        Analyze this business: {url}
        SEO: {seo}, Speed: {perf}
        Content: {web_text}

        You MUST provide exactly three sections starting with these exact markers:
        [AUDIT]
        (Write the business audit here)
        
        [WHATSAPP]
        (Write the WhatsApp message here)
        
        [EMAIL]
        (Write the Email campaign here)
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"TECHNICAL ERROR: {str(e)}"

# 4. THE USER INTERFACE
target_url = st.text_input("Enter Business Website (e.g., https://example.com)")

if st.button("Generate Audit & Outreach"):
    if not gemini_key or not google_key:
        st.error("Please provide both API keys in the sidebar.")
    else:
        with st.spinner("Analyzing..."):
            seo_score, perf_score = get_audit_data(target_url, google_key)
            result_text = analyze_with_ai(target_url, seo_score, perf_score, gemini_key)
            
            if "TECHNICAL ERROR" in result_text:
                st.error(result_text)
            else:
                # ADVANCED PARSING LOGIC
                # We search for the markers instead of just splitting by dashes
                def extract_section(text, start_marker, end_marker=None):
                    try:
                        start = text.find(start_marker) + len(start_marker)
                        if end_marker:
                            end = text.find(end_marker)
                            return text[start:end].strip()
                        return text[start:].strip()
                    except:
                        return "Content not found in AI response. Try again."

                audit_content = extract_section(result_text, "[AUDIT]", "[WHATSAPP]")
                whatsapp_content = extract_section(result_text, "[WHATSAPP]", "[EMAIL]")
                email_content = extract_section(result_text, "[EMAIL]")

                # If parsing fails, show the whole thing in the first tab
                if not audit_content or len(audit_content) < 10:
                    audit_content = result_text

                st.success("Analysis Complete!")
                
                t1, t2, t3 = st.tabs(["📊 Business Audit", "💬 WhatsApp Pitch", "✉️ Email Outreach"])
                
                with t1:
                    st.write(f"**SEO Score:** {seo_score} | **Speed:** {perf_score}")
                    st.markdown(audit_content)
                    # PDF Download
                    try:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Helvetica", size=12)
                        pdf.multi_cell(0, 10, txt=audit_content.encode('latin-1', 'ignore').decode('latin-1'))
                        st.download_button("Download PDF", bytes(pdf.output()), "Audit.pdf", "application/pdf")
                    except: st.info("Copy text manually.")

                with t2:
                    st.code(whatsapp_content, language="text")

                with t3:
                    st.code(email_content, language="text")
