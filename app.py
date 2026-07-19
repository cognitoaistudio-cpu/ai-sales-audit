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
    st.info("I will automatically find the best available model for your account.")

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
        
        # --- SMART MODEL DISCOVERY ---
        # This lists all models your key is allowed to use
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # We look for Flash models first because they are fast and have high free limits
        best_model = None
        for m_name in available_models:
            if "flash" in m_name.lower():
                best_model = m_name
                break
        
        if not best_model:
            best_model = available_models[0] # Fallback to first available

        st.info(f"Connected using: {best_model}")
        model = genai.GenerativeModel(best_model)
        
        # Scrape Website
        scrape_url = f"https://r.jina.ai/{url}"
        web_text = requests.get(scrape_url).text[:3500] # Use 3500 to stay under token limits
        
        prompt = f"""
        Act as a Direct Response Marketing Expert (think Gary Halbert or Dan Kennedy).
        Analyze this business: {url}
        Data: SEO {seo}, Speed {perf}. 
        Content: {web_text}
        
        Provide the following sections clearly labeled with '---':

        ---REPORT---
        Perform a professional digital audit. Identify 'Leaking Revenue' (missing chatbots, slow speed, no booking). 
        Use bullet points.

        ---WHATSAPP---
        Create a short, high-conversion WhatsApp message. 
        Structure: 1. Personalized observation. 2. The 'Gap'. 3. Low-friction CTA.
        Use emojis. Max 50 words.

        ---EMAIL---
        Subject Line: (Give 2 punchy options)
        Body: Use the PAS (Problem, Agitate, Solve) framework. 
        Focus on 'Real World Proof'—explain why companies with AI booking grow 20% faster.
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"TECHNICAL ERROR: {str(e)}"

# 4. THE USER INTERFACE
target_url = st.text_input("Enter Business Website (e.g., https://example.com)")

if st.button("Generate Audit & Outreach"):
    if not gemini_key or not google_key:
        st.error("Please add keys in the sidebar.")
    else:
        with st.spinner("AI is analyzing the business..."):
            seo_score, perf_score = get_audit_data(target_url, google_key)
            full_text = analyze_and_write(target_url, seo_score, perf_score, gemini_key)
            
            if "TECHNICAL ERROR" in full_text:
                st.error(full_text)
            else:
                # SPLITTING INTO TABS
                sections = full_text.split("---")
                audit_out = ""
                wa_out = ""
                email_out = ""
                
                for s in sections:
                    if "REPORT" in s: audit_out = s.replace("REPORT", "").strip()
                    if "WHATSAPP" in s: wa_out = s.replace("WHATSAPP", "").strip()
                    if "EMAIL" in s: email_out = s.replace("EMAIL", "").strip()

                st.success("Analysis Complete!")
                t1, t2, t3 = st.tabs(["📊 Audit Report", "💬 WhatsApp Pitch", "✉️ Email Campaign"])
                
                with t1:
                    st.write(f"**SEO Score:** {seo_score} | **Speed:** {perf_score}")
                    st.markdown(audit_out)
                    try:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Helvetica", size=12)
                        clean = audit_out.encode('latin-1', 'ignore').decode('latin-1')
                        pdf.multi_cell(0, 10, txt=clean)
                        st.download_button("📩 Download PDF Report", bytes(pdf.output()), "Audit.pdf", "application/pdf")
                    except: st.write("Copy report text manually.")

                with t2:
                    st.subheader("WhatsApp Pitch (Short & Crisp)")
                    st.code(wa_out, language="text")
                    st.caption("Copy and paste this into WhatsApp Web.")

                with t3:
                    st.subheader("Email Pitch (High Conversion)")
                    st.code(email_out, language="text")
                    st.caption("Use Subject Line 1 for highest open rates.")
