import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Lead Generation UI", layout="wide")

st.title("🔎 Lead Generation UI (n8n + Streamlit)")

st.write("Paste LinkedIn profile URLs below (one per line):")

urls_input = st.text_area("LinkedIn URLs", height=200)

n8n_webhook_url = "http://localhost:5678/webhook/f602284d-dbc6-4834-9e8d-4b8929fdb928"

if st.button("Run Lead Generation"):
    if not urls_input.strip():
        st.error("Please enter at least one link.")
    else:
        urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

        with st.spinner("Processing leads..."):
            try:
                response = requests.post(n8n_webhook_url, json={"urls": urls})
                
                if response.status_code != 200:
                    st.error(f"n8n Error: {response.text}")
                else:
                    data = response.json()

                    if isinstance(data, dict):
                        data = [data]

                    df = pd.DataFrame(data)

                    st.success("Lead generation completed!")

                    st.dataframe(df)

                    # Download CSV
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        "leads.csv",
                        "text/csv"
                    )

            except Exception as e:
                st.error(f"Error: {e}")
