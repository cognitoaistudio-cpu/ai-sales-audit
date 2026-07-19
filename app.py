import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF

# 1. SETUP PAGE
st.set_page_config(page_title="AI Sales Intelligence 3.0", layout="wide")
st.title("🚀 AI Sales Intelligence & Outreach")

# 2. SIDEBAR
with st.sidebar:
    st.header("⚙️ Configuration")
    gemini_key = st.text_input("Enter Gemini API Key", type="password").strip()
    google_key = st.text_input("Enter PageSpeed API Key", type="password").strip()
    
    st.divider()
    st.header("🏢 Business Context")
    # This "locks" the AI so it doesn't talk about gambling/junk
    industry = st.selectbox("Select Business Industry", 
                            ["Healthcare/Dental", "Real Estate", "Legal Services", "HVAC/Plumbing", "Education", "E-commerce", "Other"])
    
    st.info("The AI will now focus purely on this industry's specific revenue leaks.")

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

def analyze_with_ai(url, seo, perf, gemini_key, industry_type):
    try:
        genai.configure(api_key=gemini_key)
        
        # Select best model
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preferred = ['models/gemini-3-flash-preview', 'models/gemini-1.5-flash', 'models/gemini-2.0-flash']
        best_model = next((p for p in preferred if p in available_models), available_models[0])
        model = genai.GenerativeModel(best_model)
        
        # Scrape Website
        scrape_url = f"https://r.jina.ai/{url}"
        web_text = requests.get(scrape_url).text[:4000]
        
        # REFINED PROMPT: Focuses on Industry and ROI
        prompt = f"""
        Act as a Senior Business Consultant specializing in the {industry_type} industry.
        You are auditing the business website: {url}
        Current SEO Score: {seo}/100 | Speed Score: {perf}/100.
        Website Content: {web_text}

        IMPORTANT: If the website content seems irrelevant or hacked, ignore the junk and focus on providing a professional audit for a {industry_type} business based on the URL and industry standards.

        Your response MUST have these 3 exact markers:

        [AUDIT]
        Executive Summary: Analyze the digital presence for a {industry_type} business. 
        Revenue Leaks: Identify why they are losing clients (e.g., no 24/7 AI booking, slow response times, no automated FAQs).
        ROI Impact: Explain how an AI Receptionist or Agent would increase their monthly revenue.

        [WHATSAPP]
        A short, crisp, peer-to-peer message. 
        Start with a compliment, mention one specific technical gap, and ask a low-friction question. Max 50 words.

        [EMAIL]
        Subject: Quick question regarding {url}
        Body: Use the PAS (Problem, Agitate, Solve) framework. Focus on client experience and automation.
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"TECHNICAL ERROR: {str(e)}"

# 4. THE USER INTERFACE
target_url = st.text_input("Enter Business Website (e.g., https://example.com)")

if st.button("Generate Professional Audit"):
    if not gemini_key or not google_key:
        st.error("Please provide API keys in the sidebar.")
    else:
        with st.spinner(f"Analyzing {target_url} for the {industry} industry..."):
            seo_score, perf_score = get_audit_data(target_url, google_key)
            result_text = analyze_with_ai(target_url, seo_score, perf_score, gemini_key, industry)
            
            if "TECHNICAL ERROR" in result_text:
                st.error(result_text)
            else:
                # ADVANCED PARSING
                def extract_section(text, start_marker, end_marker=None):
                    try:
                        start = text.find(start_marker) + len(start_marker)
                        if end_marker:
                            end = text.find(end_marker)
                            return text[start:end].strip()
                        return text[start:].strip()
                    except: return "Section not generated. Try again."

                audit_content = extract_section(result_text, "[AUDIT]", "[WHATSAPP]")
                whatsapp_content = extract_section(result_text, "[WHATSAPP]", "[EMAIL]")
                email_content = extract_section(result_text, "[EMAIL]")

                st.success("Professional Audit Ready!")
                
                t1, t2, t3 = st.tabs(["📊 Business Audit", "💬 WhatsApp Pitch", "✉️ Email Outreach"])
                
                with t1:
                    st.write(f"### Digital Health Report: {target_url}")
                    col1, col2 = st.columns(2)
                    col1.metric("SEO Score", f"{seo_score}%")
                    col2.metric("Speed Score", f"{perf_score}%")
                    st.markdown(audit_content)
                    
                    # PDF Download
                    try:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Helvetica", size=12)
                        pdf.multi_cell(0, 10, txt=f"Audit Report for {target_url}\n\n" + audit_content.encode('latin-1', 'ignore').decode('latin-1'))
                        st.download_button("📩 Download PDF Report", bytes(pdf.output()), f"Audit_{target_url}.pdf", "application/pdf")
                    except: st.info("Copy manually if PDF fails.")

                with t2:
                    st.subheader("WhatsApp Outreach")
                    st.code(whatsapp_content, language="text")

                with t3:
                    st.subheader("Email Campaign")
                    st.code(email_content, language="text")
