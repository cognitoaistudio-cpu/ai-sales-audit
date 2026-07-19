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
    st.info("Your AI Outreach is tuned for high conversion rates.")

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
        # Dynamic model selection
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        best_model = next((m for m in ['models/gemini-1.5-flash', 'models/gemini-2.0-flash', 'models/gemini-pro'] if m in available_models), available_models[0])
        
        model = genai.GenerativeModel(best_model)
        scrape_url = f"https://r.jina.ai/{url}"
        web_text = requests.get(scrape_url).text[:4000]
        
        # MARKETING PROMPT
        prompt = f"""
        Act as a World-Class Sales Consultant and Direct Response Marketer.
        Website: {url}
        Data: SEO {seo}/100, Speed {perf}/100.
        Web Context: {web_text}

        TASK:
        1. Generate a Professional Audit Report.
        2. Generate a 'Short & Crisp' WhatsApp Pitch (include emojis, max 50 words).
        3. Generate a High-Conversion Email (3 Subject Line options + Body).
        
        MARKETING RULES:
        - Lead with the 'Gap' (what they are missing).
        - Use the PAS (Problem, Agitate, Solve) framework.
        - Focus on 'Leaking Revenue' or 'Missed Leads'.
        - Call to Action (CTA) must be low-friction (e.g., 'Open to a quick chat?').

        FORMAT:
        ---REPORT---
        (The Audit)
        ---WHATSAPP---
        (The WhatsApp message)
        ---EMAIL---
        (The Email)
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
        with st.spinner("Analyzing & Writing your pitch..."):
            seo_score, perf_score = get_audit_data(target_url, google_key)
            full_response = analyze_and_write(target_url, seo_score, perf_score, gemini_key)
            
            if "TECHNICAL ERROR" in full_response:
                st.error(full_response)
            else:
                # SPLITTING THE DATA
                try:
                    parts = full_response.split("---")
                    audit_content = parts[2].replace("REPORT---", "").strip()
                    whatsapp_content = parts[4].replace("WHATSAPP---", "").strip()
                    email_content = parts[6].replace("EMAIL---", "").strip()
                except:
                    # Fallback if split fails
                    audit_content, whatsapp_content, email_content = full_response, "Error splitting", "Error splitting"

                st.success("Audit & Outreach Generated!")
                
                # UI TABS
                tab1, tab2, tab3 = st.tabs(["📊 Audit Report", "💬 WhatsApp Pitch", "✉️ Email Campaign"])
                
                with tab1:
                    st.write(f"**SEO:** {seo_score} | **Speed:** {perf_score}")
                    st.markdown(audit_content)
                    # PDF Download
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", size=12)
                    pdf.multi_cell(0, 10, txt=f"Audit for {target_url}\n\n" + audit_content.encode('latin-1', 'ignore').decode('latin-1'))
                    st.download_button("📩 Download PDF Report", bytes(pdf.output()), "Audit.pdf", "application/pdf")

                with tab2:
                    st.info("Click the copy icon in the top right of the box below.")
                    st.code(whatsapp_content, language="text")
                    st.caption("Pro Tip: Send this to the business owner on WhatsApp for the fastest response.")

                with tab3:
                    st.info("Copy-paste this into your email provider.")
                    st.code(email_content, language="text")
                    st.caption("Pro Tip: Use the first subject line for the highest open rates.")
