import streamlit as st
import requests
import google.generativeai as genai
from fpdf import FPDF
import re

# 1. COGNITO AI BRANDING & SETUP
st.set_page_config(page_title="Cognito AI Sales Copilot", layout="wide", page_icon="🤖")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .report-box { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Cognito AI Sales Copilot")
st.subheader("Automated Business Intelligence & Audit Platform")

# 2. SIDEBAR - MODULE 1: BUSINESS PROFILE
with st.sidebar:
    st.header("🏢 Module 1: Profile")
    biz_name = st.text_input("Business Name")
    target_url = st.text_input("Website URL (https://...)")
    city = st.text_input("City")
    industry = st.selectbox("Industry", ["Healthcare", "Real Estate", "Legal", "Home Services", "Retail", "Other"])
    
    st.divider()
    st.header("🔑 API Keys")
    gemini_key = st.text_input("Gemini API Key", type="password").strip()
    google_key = st.text_input("PageSpeed API Key", type="password").strip()

# 3. AUDIT ENGINE LOGIC
def perform_technical_audit(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=SEO&category=PERFORMANCE&category=ACCESSIBILITY&category=BEST_PRACTICES&key={api_key}"
    try:
        r = requests.get(api_url).json()
        lh = r['lighthouseResult']['categories']
        return {
            "seo": lh['seo']['score'] * 100,
            "speed": lh['performance']['score'] * 100,
            "access": lh['accessibility']['score'] * 100,
            "best": lh['best-practices']['score'] * 100,
            "mobile": r['lighthouseResult']['configSettings']['formFactor']
        }
    except:
        return None

def detect_ai_readiness(html_text):
    # Search for common signatures
    patterns = {
        "Chatbot": r"(intercom|drift|tidio|crisp|chat|messenger)",
        "WhatsApp": r"(wa\.me|whatsapp|api\.whatsapp)",
        "Booking": r"(calendly|acuity|booker|appointment|resurva)",
        "CRM/Forms": r"(hubspot|marketo|salesforce|contact-form|lead-capture)",
        "Payments": r"(stripe|paypal|checkout|pay)"
    }
    results = {}
    for tech, pattern in patterns.items():
        results[tech] = bool(re.search(pattern, html_text.lower()))
    return results

# 4. AI ANALYSIS ENGINE (GEMINI 3)
def generate_copilot_report(biz_data, tech_data, ai_ready, web_content, gemini_key):
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")
    
    prompt = f"""
    You are the Cognito AI Sales Copilot. Perform a deep audit for {biz_data['name']} in {biz_data['city']}.
    
    DATA:
    - Technical Scores: SEO {tech_data['seo']}, Speed {tech_data['speed']}, Accessibility {tech_data['access']}
    - Tech Detected: {ai_ready}
    - Content Snippet: {web_content[:3000]}

    YOUR TASK: Generate a high-end Agency Report.
    
    Format the output in exactly these sections:
    
    [AI_SCORE]
    Calculate a score out of 100 for 'AI Readiness'. List 6 specific items with ✅ or ❌.
    
    [OPPORTUNITIES]
    List 4 specific 'Opportunity Detection' statements. (e.g. "Website visitors have no immediate way to ask questions after business hours.")
    
    [ROI]
    Provide a table-style ROI Estimator showing Potential Impact of AI Automation.
    
    [ROADMAP]
    A 3-step implementation roadmap to move the business to an AI-First model.
    """
    
    response = model.generate_content(prompt)
    return response.text

# 5. EXECUTION UI
if st.button("🚀 Run Full Cognito Audit"):
    if not gemini_key or not google_key or not target_url:
        st.error("Missing inputs. Please check Profile and API keys.")
    else:
        with st.spinner("Module 2 & 3: Scanning Website & SEO..."):
            tech_data = perform_technical_audit(target_url, google_key)
            
        with st.spinner("Module 4: Detecting AI Readiness..."):
            scrape_url = f"https://r.jina.ai/{target_url}"
            web_raw = requests.get(scrape_url).text
            ai_ready = detect_ai_readiness(web_raw)
            
        if tech_data:
            with st.spinner("Generating Copilot Intelligence..."):
                report = generate_copilot_report(
                    {"name": biz_name, "city": city}, 
                    tech_data, ai_ready, web_raw, gemini_key
                )
                
                # PARSING THE REPORT
                def get_sec(t, m):
                    try: return t.split(m)[1].split("[")[0].strip()
                    except: return "Data missing."

                st.success("Audit Complete!")
                
                # --- VISUAL DASHBOARD ---
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("SEO Score", f"{tech_data['seo']}%")
                col2.metric("Speed", f"{tech_data['speed']}%")
                col3.metric("Accessibility", f"{tech_data['access']}%")
                col4.metric("Best Practices", f"{tech_data['best']}%")

                t1, t2, t3, t4 = st.tabs(["🎯 AI Readiness", "💡 Opportunities", "📈 ROI Estimator", "🗺️ Roadmap"])
                
                with t1:
                    st.markdown("### Module 4: AI Readiness Score")
                    st.markdown(get_sec(report, "[AI_SCORE]"))
                    
                with t2:
                    st.markdown("### Module 6: Opportunity Detection")
                    st.markdown(get_sec(report, "[OPPORTUNITIES]"))
                    
                with t3:
                    st.markdown("### Module 7: ROI Estimator")
                    st.info("Assumptions based on industry standards for " + industry)
                    st.markdown(get_sec(report, "[ROI]"))
                    
                with t4:
                    st.markdown("### Module 8: Implementation Roadmap")
                    st.markdown(get_sec(report, "[ROADMAP]"))
                    
                    # PDF GENERATION
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(200, 10, txt=f"COGNITO AI AUDIT: {biz_name}", ln=True, align='C')
                    pdf.set_font("Arial", size=12)
                    pdf.multi_cell(0, 10, txt=report.encode('latin-1', 'ignore').decode('latin-1'))
                    st.download_button("📩 Download Professional PDF Report", bytes(pdf.output()), "Cognito_Audit.pdf")

        else:
            st.error("Technical scan failed. Check the URL and Google API Key.")
