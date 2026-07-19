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
    st.info("Stability Mode: Active. (Trying multiple models to bypass Google errors)")

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
        
        # WATERFALL LIST: We try these in order. 
        # 1.5-flash is the most stable free model globally.
        model_names = [
            'gemini-1.5-flash', 
            'gemini-1.5-pro', 
            'gemini-2.0-flash-exp', 
            'models/gemini-1.5-flash'
        ]
        
        scrape_url = f"https://r.jina.ai/{url}"
        web_text = requests.get(scrape_url).text[:3000]
        
        prompt = f"""
        Act as a Direct Response Marketing Expert.
        Analyze business: {url}
        Data: SEO {seo}, Speed {perf}. 
        Content: {web_text}
        
        ---REPORT---
        Audit the site for missing AI/automation and revenue leaks.
        ---WHATSAPP---
        Short, high-conversion WhatsApp message with emojis (max 50 words).
        ---EMAIL---
        3 Subject Line options.
        Body: Use PAS (Problem, Agitate, Solve) framework.
        """

        # THE WATERFALL LOOP
        response_text = ""
        success = False
        for m_name in model_names:
            try:
                model = genai.GenerativeModel(m_name)
                response = model.generate_content(prompt)
                response_text = response.text
                success = True
                st.sidebar.success(f"Connected via {m_name}")
                break # Exit loop if it works
            except Exception as e:
                continue # Try the next model in the list
        
        if not success:
            return "TECHNICAL ERROR: All Google models are currently busy or unavailable. Please check your API key or wait 60 seconds."
            
        return response_text

    except Exception as e:
        return f"TECHNICAL ERROR: {str(e)}"

# 4. THE USER INTERFACE
target_url = st.text_input("Enter Business Website (e.g., https://example.com)")

if st.button("Generate Audit & Outreach"):
    if not gemini_key or not google_key:
        st.error("Please add keys in the sidebar.")
    else:
        with st.spinner("AI is bypassing Google errors and analyzing..."):
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
                    except: st.write("Use copy-paste for report.")

                with t2:
                    st.subheader("WhatsApp Pitch (Direct & Short)")
                    st.code(wa_out, language="text")
                    st.caption("Perfect for cold outreach on WhatsApp.")

                with t3:
                    st.subheader("Email Pitch (Marketing Framework)")
                    st.code(email_out, language="text")
                    st.caption("Designed to hit pain points and trigger replies.")
