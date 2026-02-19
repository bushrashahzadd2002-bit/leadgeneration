import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Lead Generation", layout="wide")

st.title("Lead Generation")

st.write("Paste LinkedIn profile URLs below (one per line):")

urls_input = st.text_area("LinkedIn URLs", height=200)

n8n_webhook_url = "https://aiuhf.app.n8n.cloud/webhook/88ea4c9b-b24b-4f79-b553-338914ba83f1"

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
