import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF

st.set_page_config(page_title="AI Sales Auditor", layout="wide")
st.title("🚀 AI Sales Intelligence & Outreach")

# 1. SIDEBAR SETUP
with st.sidebar:
    st.header("Setup")
    gemini_key = st.text_input("Enter Gemini API Key", type="password").strip()
    google_key = st.text_input("Enter PageSpeed API Key", type="password").strip()
    
    st.divider()
    # MANUAL MODEL PICKER - If one fails, user can pick another
    st.subheader("AI Settings")
    model_choice = st.selectbox(
        "Select AI Model",
        ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
        help="If you get a 404 error, try switching to gemini-1.5-flash"
    )
    st.info("Tip: gemini-1.5-flash is usually the most stable free model.")

# 2. THE AI FUNCTION
def run_ai_audit(target_url, seo, perf, api_key, model_name):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        # Get Website Data
        scrape_url = f"https://r.jina.ai/{target_url}"
        try:
            web_content = requests.get(scrape_url, timeout=10).text[:3000]
        except:
            web_content = "Unable to read website content."
        
        prompt = f"""
        Act as a Sales Marketer. 
        Audit this business: {target_url}
        Data: SEO {seo}, Speed {perf}
        Website Content: {web_content}
        
        Format your response exactly as follows:
        ---REPORT---
        (Detailed business audit with revenue leaks)
        ---WHATSAPP---
        (Short pitch with emojis)
        ---EMAIL---
        (Subject + PAS framework body)
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"ERROR: {str(e)}"

# 3. THE UI
target_url = st.text_input("Enter Website URL (e.g., https://example.com)")

if st.button("Generate Audit & Outreach"):
    if not gemini_key or not google_key:
        st.warning("Please enter both API keys in the sidebar.")
    else:
        with st.spinner(f"Using {model_choice} to analyze..."):
            # 1. Get PageSpeed Data
            ps_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={target_url}&category=SEO&category=PERFORMANCE&key={google_key}"
            try:
                r = requests.get(ps_url).json()
                seo = r['lighthouseResult']['categories']['seo']['score'] * 100
                perf = r['lighthouseResult']['categories']['performance']['score'] * 100
            except:
                seo, perf = "N/A", "N/A"

            # 2. Run AI Audit
            result = run_ai_audit(target_url, seo, perf, gemini_key, model_choice)
            
            if "ERROR" in result:
                st.error(result)
                st.info("Try selecting a different model in the sidebar and clicking the button again.")
            else:
                st.success("Audit & Outreach Ready!")
                
                # Split result safely
                parts = result.split("---")
                # Default empty content
                report_text = result
                wa_text = "Message generation failed. Copy from report."
                email_text = "Message generation failed. Copy from report."
                
                # Assign parts based on labels
                for part in parts:
                    if "REPORT" in part: report_text = part.replace("REPORT", "").strip()
                    if "WHATSAPP" in part: wa_text = part.replace("WHATSAPP", "").strip()
                    if "EMAIL" in part: email_text = part.replace("EMAIL", "").strip()

                # TABS
                tab1, tab2, tab3 = st.tabs(["📊 Audit Report", "💬 WhatsApp Pitch", "✉️ Email Campaign"])
                
                with tab1:
                    st.metric("SEO Score", f"{seo}%")
                    st.metric("Speed Score", f"{perf}%")
                    st.markdown(report_text)
                    # Simple PDF button
                    try:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        pdf.multi_cell(0, 10, txt=report_text.encode('latin-1', 'ignore').decode('latin-1'))
                        st.download_button("📩 Download PDF", bytes(pdf.output()), "Audit.pdf", "application/pdf")
                    except: pass

                with tab2:
                    st.subheader("WhatsApp Message")
                    st.code(wa_text, language="text")
                    st.caption("Click the icon top-right to copy.")

                with tab3:
                    st.subheader("Email Pitch")
                    st.code(email_text, language="text")
