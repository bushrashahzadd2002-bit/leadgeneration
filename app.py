import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="LinkedIn Lead Generation", layout="wide", page_icon="🎯")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #0077B5, #00A0DC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #0077B5, #00A0DC);
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 8px;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #005582, #0077B5);
    }
    .stat-box {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid #0077B5;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0077B5;
    }
    .stat-label {
        color: #666;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎯 LinkedIn Lead Generation</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Extract professional data from LinkedIn profiles automatically</div>', unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")

# Check n8n status
n8n_base = "http://localhost:5678"
n8n_status = "🔴 Not Running"
try:
    requests.get(n8n_base, timeout=2)
    n8n_status = "🟢 Running"
except:
    pass

st.sidebar.info(f"**n8n Status:** {n8n_status}")

# Webhook URL input
n8n_webhook_url = st.sidebar.text_input(
    "Webhook URL",
    value="http://localhost:5678/webhook/f602284d-dbc6-4834-9e8d-4b8929fdb928",
    help="Production webhook URL from your n8n workflow"
)

# Warning for test URL
if "/webhook-test/" in n8n_webhook_url:
    st.sidebar.error("⚠️ **Test URL detected!** Remove '-test' from the URL")

# Test webhook button
if st.sidebar.button("🔌 Test Webhook Connection"):
    with st.spinner("Testing connection..."):
        try:
            response = requests.post(
                n8n_webhook_url,
                json={"urls": ["https://linkedin.com/in/test"]},
                timeout=10
            )
            if response.status_code == 200:
                st.sidebar.success("✅ Webhook is active and responding!")
            else:
                st.sidebar.warning(f"⚠️ Got response but status {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.sidebar.error("❌ Can't connect. Is n8n running and workflow active?")
        except requests.exceptions.Timeout:
            st.sidebar.warning("⏱️ Timeout - workflow might be processing")
        except Exception as e:
            st.sidebar.error(f"❌ Error: {str(e)[:100]}")

st.sidebar.divider()

# Instructions
with st.sidebar.expander("📖 How to Use"):
    st.markdown("""
    ### Setup Steps:
    
    1. **Start n8n:**
       ```bash
       n8n start
       ```
    
    2. **Activate your workflow** in n8n
    
    3. **Copy Production URL** from Webhook node
    
    4. **Paste URLs** (one per line):
       - https://linkedin.com/in/username1
       - https://linkedin.com/in/username2
    
    5. **Click "Generate Leads"** and wait
    
    ### What it extracts:
    - ✅ Full Name
    - ✅ Current Company
    - ✅ Industry
    - ✅ Email Address
    - ✅ Saves to Google Sheets
    """)

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 LinkedIn Profile URLs")
    urls_input = st.text_area(
        "",
        height=300,
        placeholder="Paste LinkedIn profile URLs here (one per line):\n\nhttps://linkedin.com/in/example1\nhttps://linkedin.com/in/example2\nhttps://linkedin.com/in/example3",
        label_visibility="collapsed"
    )
    
    # Quick example button
    if st.button("📋 Load Example URLs"):
        example_urls = """https://linkedin.com/in/williamhgates
https://linkedin.com/in/satyanadella
https://linkedin.com/in/jeffweiner08"""
        st.session_state.example_urls = example_urls
        st.rerun()
    
    if 'example_urls' in st.session_state:
        urls_input = st.session_state.example_urls
        del st.session_state.example_urls

with col2:
    st.subheader("📊 Quick Stats")
    
    # Count URLs
    url_count = len([u for u in urls_input.split("\n") if u.strip()])
    
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{url_count}</div>
        <div class="stat-label">URLs Ready</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Estimated time (rough estimate: 10-15 sec per profile)
    est_time = url_count * 12  # seconds
    if est_time > 60:
        time_str = f"{est_time // 60}m {est_time % 60}s"
    else:
        time_str = f"{est_time}s"
    
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">~{time_str}</div>
        <div class="stat-label">Est. Processing Time</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Generate Button
if st.button("🚀 Generate Leads", type="primary", disabled=(url_count == 0)):
    if not urls_input.strip():
        st.error("❌ Please enter at least one LinkedIn URL")
    else:
        urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
        
        # Validate URLs
        valid_urls = []
        invalid_urls = []
        for url in urls:
            if "linkedin.com/in/" in url:
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        
        if invalid_urls:
            st.warning(f"⚠️ Skipping {len(invalid_urls)} invalid URL(s)")
            with st.expander("Show invalid URLs"):
                for url in invalid_urls:
                    st.text(f"❌ {url}")
        
        if not valid_urls:
            st.error("❌ No valid LinkedIn URLs found")
        else:
            st.info(f"🔄 Processing {len(valid_urls)} LinkedIn profile(s)...")
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            start_time = time.time()
            
            try:
                status_text.text("⏳ Sending request to n8n workflow...")
                progress_bar.progress(10)
                
                # Debug info
                st.info(f"🔍 Sending to: `{n8n_webhook_url}`")
                
                response = requests.post(
                    n8n_webhook_url,
                    json={"urls": valid_urls},
                    timeout=600,  # 10 minute timeout
                    headers={"Content-Type": "application/json"}
                )
                
                progress_bar.progress(50)
                status_text.text("🤖 n8n is processing profiles...")
                
                elapsed = time.time() - start_time
                
                if response.status_code != 200:
                    st.error(f"❌ n8n Error (Status {response.status_code})")
                    with st.expander("Show error details"):
                        st.code(response.text)
                    progress_bar.empty()
                    status_text.empty()
                else:
                    progress_bar.progress(90)
                    status_text.text("✨ Formatting results...")
                    
                    data = response.json()
                    
                    # Handle different response formats
                    if isinstance(data, dict):
                        if 'data' in data:
                            data = data['data']
                        else:
                            data = [data]
                    
                    if not data:
                        st.warning("⚠️ No data returned from workflow")
                    else:
                        df = pd.DataFrame(data)
                        
                        progress_bar.progress(100)
                        status_text.empty()
                        
                        # Success message
                        st.success(f"✅ Successfully processed {len(df)} lead(s) in {elapsed:.1f} seconds!")
                        
                        # Display results
                        st.subheader("📋 Extracted Leads")
                        
                        # Format dataframe
                        if 'email' in df.columns:
                            df['email'] = df['email'].apply(lambda x: f"✉️ {x}" if pd.notna(x) else "❌ Not found")
                        
                        st.dataframe(
                            df,
                            use_container_width=True,
                            height=400
                        )
                        
                        # Download options
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv,
                                file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        
                        with col2:
                            excel_buffer = pd.ExcelWriter('temp.xlsx', engine='xlsxwriter')
                            df.to_excel(excel_buffer, index=False, sheet_name='Leads')
                            excel_buffer.close()
                            
                            st.download_button(
                                label="📊 Download Excel",
                                data=open('temp.xlsx', 'rb').read(),
                                file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        
                        with col3:
                            st.markdown(f"**✅ Saved to Google Sheets**")
                        
                        # Show summary stats
                        st.divider()
                        st.subheader("📈 Summary")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Leads", len(df))
                        
                        with col2:
                            emails_found = df['email'].notna().sum() if 'email' in df.columns else 0
                            st.metric("Emails Found", emails_found)
                        
                        with col3:
                            companies = df['company'].nunique() if 'company' in df.columns else 0
                            st.metric("Unique Companies", companies)
                        
                        with col4:
                            st.metric("Processing Time", f"{elapsed:.1f}s")
                
            except requests.exceptions.ConnectionError as e:
                progress_bar.empty()
                status_text.empty()
                st.error("❌ **Connection Failed**")
                
                # Show detailed error
                st.code(f"Error details: {str(e)}")
                
                # Check if n8n is actually running
                try:
                    test_response = requests.get("http://localhost:5678", timeout=2)
                    st.success("✅ n8n IS running on localhost:5678")
                    st.error("❌ But the webhook URL is not responding!")
                    
                    st.markdown("""
                    ### The webhook is not registered. Here's what to check:
                    
                    1. **Is your workflow ACTIVE?**
                       - Go to http://localhost:5678
                       - Look at top right corner
                       - The toggle must be ON (blue/green)
                    
                    2. **Are you using the PRODUCTION URL?**
                       - Click on your Webhook node
                       - Copy the **Production URL** (appears after activating)
                       - Should look like: `http://localhost:5678/webhook/...`
                       - NOT: `http://localhost:5678/webhook-test/...`
                    
                    3. **Try this in terminal:**
                    """)
                    
                    st.code(f"""curl -X POST {n8n_webhook_url} \\
  -H "Content-Type: application/json" \\
  -d '{{"urls": ["https://linkedin.com/in/test"]}}'""", language="bash")
                    
                except:
                    st.markdown("""
                    ### n8n is not running or not accessible
                    
                    **Quick Fix:**
                    1. Open terminal and run: `n8n start`
                    2. Go to http://localhost:5678
                    3. Make sure your workflow is **ACTIVE** (toggle in top right)
                    4. Use the **Production** webhook URL (without '-test')
                    """)
                
            except requests.exceptions.Timeout:
                progress_bar.empty()
                status_text.empty()
                st.error("⏱️ **Request Timed Out**")
                st.info("The workflow might still be processing. Check your Google Sheets or n8n execution history.")
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ **Unexpected Error**")
                st.code(str(e))
                
                if "JSON" in str(e):
                    st.info("💡 The webhook might not be returning proper JSON. Check your n8n workflow response format.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🔧 Powered by n8n + Streamlit | 🎯 Made for Lead Generation</p>
    <p style="font-size: 0.8rem;">Make sure n8n is running and your workflow is active before generating leads</p>
</div>
""", unsafe_allow_html=True)
