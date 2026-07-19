import streamlit as st
import google.generativeai as genai
import requests
from fpdf import FPDF

st.set_page_config(page_title="AI Sales Auditor", layout="wide")
st.title("🚀 AI Sales Intelligence Platform")

# 1. SIDEBAR SETUP
with st.sidebar:
    st.header("Setup")
    # We strip spaces to prevent "Paste Errors"
    gemini_key = st.text_input("Enter Gemini API Key", type="password").strip()
    google_key = st.text_input("Enter PageSpeed API Key", type="password").strip()
    st.divider()
    st.info("Ensure your API key is from a personal @gmail.com account for best results.")

# 2. THE AI BRAIN
def run_ai_audit(target_url, seo, perf, api_key):
    try:
        genai.configure(api_key=api_key)
        
        # This part asks Google exactly what models you are allowed to use
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            return "ERROR: No AI models found for this key. Please check your Google AI Studio settings."

        # Pick the best one (prefer Flash if available)
        selected_model = available_models[0]
        for m in available_models:
            if "1.5-flash" in m:
                selected_model = m
                break
        
        st.write(f"📡 *System: Connected to {selected_model}*")
        
        model = genai.GenerativeModel(selected_model)
        
        # Get Website Data via Jina
        scrape_url = f"https://r.jina.ai/{target_url}"
        web_content = requests.get(scrape_url).text[:3000]
        
        prompt = f"""
        Identify revenue leaks for this business: {target_url}
        Data: SEO {seo}, Performance {perf}
        Content: {web_content}
        
        Format your response exactly like this:
        ---REPORT---
        (Detailed Audit)
        ---WHATSAPP---
        (Short pitch)
        ---EMAIL---
        (Subject + Body)
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"ERROR: {str(e)}"

# 3. THE UI
target_url = st.text_input("Enter Website (e.g., https://example.com)")

if st.button("Generate Audit"):
    if not gemini_key or not google_key:
        st.warning("Please enter your keys in the sidebar.")
    else:
        with st.spinner("Analyzing..."):
            # Simple PageSpeed Call
            ps_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={target_url}&category=SEO&category=PERFORMANCE&key={google_key}"
            try:
                r = requests.get(ps_url).json()
                seo = r['lighthouseResult']['categories']['seo']['score'] * 100
                perf = r['lighthouseResult']['categories']['performance']['score'] * 100
            except:
                seo, perf = "N/A", "N/A"

            # Run AI
            result = run_ai_audit(target_url, seo, perf, gemini_key)
            
            if "ERROR" in result:
                st.error(result)
            else:
                st.success("Audit Ready!")
                
                # Split result safely
                try:
                    parts = result.split("---")
                    report_text = parts[2] if len(parts) > 2 else result
                    wa_text = parts[4] if len(parts) > 4 else "N/A"
                    email_text = parts[6] if len(parts) > 6 else "N/A"
                except:
                    report_text, wa_text, email_text = result, "N/A", "N/A"

                t1, t2, t3 = st.tabs(["Report", "WhatsApp", "Email"])
                with t1:
                    st.write(f"SEO: {seo} | Speed: {perf}")
                    st.markdown(report_text)
                with t2:
                    st.code(wa_text)
                with t3:
                    st.code(email_text)
