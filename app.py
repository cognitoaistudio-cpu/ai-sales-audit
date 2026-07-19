import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF

# 1. SETUP PAGE
st.set_page_config(page_title="AI Sales Intelligence 3.0", layout="wide")
st.title("🚀 AI Sales Intelligence (Gemini 3 Powered)")

# 2. SIDEBAR SETUP
with st.sidebar:
    st.header("🔑 API Setup")
    gemini_key = st.text_input("Enter Gemini API Key", type="password").strip()
    google_key = st.text_input("Enter PageSpeed API Key", type="password").strip()
    
    st.divider()
    st.subheader("🤖 Current Model")
    st.success("gemini-3-flash-preview")
    st.caption("Optimized for complex business reasoning.")

# 3. CORE FUNCTIONS
def run_gemini3_audit(target_url, seo, perf, api_key):
    try:
        genai.configure(api_key=api_key)
        
        # Hardcoded to Gemini 3 Flash Preview as requested
        model_name = "gemini-3-flash-preview"
        model = genai.GenerativeModel(model_name)
        
        # Get Website Context via Jina
        scrape_url = f"https://r.jina.ai/{target_url}"
        try:
            web_content = requests.get(scrape_url, timeout=12).text[:4000]
        except:
            web_content = "Website text could not be extracted."

        # GEMINI 3 OPTIMIZED PROMPT
        # We use Gemini 3's advanced reasoning to find deep revenue leaks
        prompt = f"""
        System: You are an elite Business Growth Consultant using Gemini 3 Reasoning.
        Task: Analyze {target_url} for a high-ticket sales audit.
        
        Data: SEO Score {seo}/100, Performance {perf}/100.
        Context: {web_content}

        Instructions:
        1. Identify the 'Invisible Gap' - where is this business losing money that they don't see?
        2. Look for missing AI Agents (Receptionists, Lead Qualifiers, Support Bots).
        3. Create outreach that sounds like a peer, not a bot.

        Format exactly with '---':
        ---REPORT---
        (The Professional Audit)
        ---WHATSAPP---
        (Crisp, emoji-rich, PAS-style message)
        ---EMAIL---
        (3 Subject Lines + High-conversion body)
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        if "404" in str(e):
            return "ERROR: Model 'gemini-3-flash-preview' not found in your region. Check Google AI Studio for the exact name."
        return f"ERROR: {str(e)}"

# 4. THE UI
target_url = st.text_input("Enter Business URL (e.g., https://example.com)")

if st.button("Generate Gemini 3 Audit"):
    if not gemini_key or not google_key:
        st.warning("Please enter your API keys in the sidebar.")
    else:
        with st.spinner("Gemini 3 is thinking... (Analyzing deeper than ever)"):
            # 1. PageSpeed Call
            ps_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={target_url}&category=SEO&category=PERFORMANCE&key={google_key}"
            try:
                r = requests.get(ps_url).json()
                seo_val = r['lighthouseResult']['categories']['seo']['score'] * 100
                perf_val = r['lighthouseResult']['categories']['performance']['score'] * 100
            except:
                seo_val, perf_val = "N/A", "N/A"

            # 2. Gemini 3 Call
            raw_result = run_gemini3_audit(target_url, seo_val, perf_val, gemini_key)
            
            if "ERROR" in raw_result:
                st.error(raw_result)
            else:
                st.success("Gemini 3 Audit Complete!")
                
                # Split parts
                parts = raw_result.split("---")
                audit_part = ""
                wa_part = ""
                email_part = ""
                
                for p in parts:
                    if "REPORT" in p: audit_part = p.replace("REPORT", "").strip()
                    if "WHATSAPP" in p: wa_part = p.replace("WHATSAPP", "").strip()
                    if "EMAIL" in p: email_part = p.replace("EMAIL", "").strip()

                # TABS
                t1, t2, t3 = st.tabs(["📊 Deep Audit", "💬 WhatsApp Pitch", "✉️ Email Outreach"])
                
                with t1:
                    col1, col2 = st.columns(2)
                    col1.metric("SEO Health", f"{seo_val}%")
                    col2.metric("Load Speed", f"{perf_val}%")
                    st.markdown(audit_part)
                    
                    # PDF Generation
                    try:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Helvetica", size=12)
                        pdf_clean = audit_part.encode('latin-1', 'ignore').decode('latin-1')
                        pdf.multi_cell(0, 10, txt=f"Gemini 3 Audit: {target_url}\n\n" + pdf_clean)
                        st.download_button("📩 Download PDF Report", bytes(pdf.output()), f"Audit_{target_url}.pdf", "application/pdf")
                    except: st.info("Copy report manually.")

                with t2:
                    st.code(wa_part, language="text")
                    st.caption("Short and punchy for direct messaging.")

                with t3:
                    st.code(email_part, language="text")
                    st.caption("Professional outreach with Subject Line options.")
