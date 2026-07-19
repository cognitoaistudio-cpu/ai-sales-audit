import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF

# 1. SETUP PAGE
st.set_page_config(page_title="AI Sales Intelligence 3.0", layout="wide")
st.title("🚀 AI Sales Intelligence & Outreach Platform")

# 2. SIDEBAR
with st.sidebar:
    st.header("Settings")
    gemini_key = st.text_input("Enter Gemini API Key", type="password").strip()
    google_key = st.text_input("Enter PageSpeed API Key", type="password").strip()
    st.divider()
    st.info("Using Gemini 3 Flash Preview for advanced marketing reasoning.")

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
        
        # FIND THE BEST MODEL (Including Gemini 3)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority list (Gemini 3 is now first)
        preferred = [
            'models/gemini-3-flash-preview', 
            'models/gemini-2.0-flash', 
            'models/gemini-1.5-flash'
        ]
        
        best_model = None
        for p in preferred:
            if p in available_models:
                best_model = p
                break
        
        if not best_model:
            best_model = available_models[0] if available_models else None
        
        if not best_model:
            return "TECHNICAL ERROR: No models available."

        st.sidebar.write(f"⚙️ Connected: {best_model}")
        model = genai.GenerativeModel(best_model)
        
        # Scrape Content
        scrape_url = f"https://r.jina.ai/{url}"
        web_text = requests.get(scrape_url).text[:4000]
        
        # ADVANCED MARKETING PROMPT
        prompt = f"""
        You are a World-Class Sales & Marketing Consultant (Expert in PAS Framework and Conversion).
        Website URL: {url}
        Data: {web_text}
        SEO Score: {seo}/100, Speed Score: {perf}/100.

        TASK: Generate a 3-part sales intelligence package. Use '---' to separate sections.

        ---REPORT---
        Write a professional audit. Identify 'Revenue Leaks'. 
        Mention that AI booking/chatbots can increase lead conversion by 20-30% based on real-world industry proofs.
        
        ---WHATSAPP---
        Write a short, crisp, personalized WhatsApp pitch. 
        - Use emojis.
        - Mention one specific technical flaw found.
        - End with a low-friction question (CTA).
        - Max 60 words.

        ---EMAIL---
        - 3 Click-worthy Subject Line options (Use 'Open Loops').
        - Body: Use PAS (Problem, Agitate, Solve) framework.
        - Mention that slow load times or manual forms are 'Silent Sales Killers'.
        - Include a clear call to action to see the full PDF audit.
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
        with st.spinner("Gemini 3 is analyzing the business and writing your pitch..."):
            seo_score, perf_score = get_audit_data(target_url, google_key)
            result = analyze_with_ai(target_url, seo_score, perf_score, gemini_key)
            
            if "TECHNICAL ERROR" in result:
                st.error(result)
            else:
                st.success("Sales Intelligence Package Ready!")
                
                # Split the results into components
                try:
                    parts = result.split("---")
                    report_content = ""
                    whatsapp_content = ""
                    email_content = ""
                    
                    for p in parts:
                        if "REPORT" in p: report_content = p.replace("REPORT", "").strip()
                        if "WHATSAPP" in p: whatsapp_content = p.replace("WHATSAPP", "").strip()
                        if "EMAIL" in p: email_content = p.replace("EMAIL", "").strip()
                except:
                    report_content, whatsapp_content, email_content = result, "Check Report", "Check Report"

                # UI TABS
                tab1, tab2, tab3 = st.tabs(["📊 Business Audit", "💬 WhatsApp Pitch", "✉️ Email Campaign"])
                
                with tab1:
                    st.write(f"**SEO:** {seo_score} | **Speed:** {perf_score}")
                    st.markdown(report_content)
                    
                    # PDF Generation
                    try:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Helvetica", size=12)
                        clean_report = report_content.encode('latin-1', 'ignore').decode('latin-1')
                        pdf.multi_cell(0, 10, txt=f"Audit for {target_url}\n\n" + clean_report)
                        st.download_button("📩 Download PDF Report", bytes(pdf.output()), "Audit_Report.pdf", "application/pdf")
                    except: st.info("Copy report manually.")

                with tab2:
                    st.subheader("Copy to WhatsApp")
                    st.info("Short & Crisp: Designed for high response rates.")
                    st.code(whatsapp_content, language="text")
                    st.caption("Pro Tip: Send this from WhatsApp Web for maximum speed.")

                with tab3:
                    st.subheader("Copy to Email")
                    st.info("Subject lines are optimized for open rates using marketing psychological triggers.")
                    st.code(email_content, language="text")
