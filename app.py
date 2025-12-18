import streamlit as st
import os
import json
import re
from openai import OpenAI

# Initialize session state for samples
if 'requirement_text' not in st.session_state:
    st.session_state.requirement_text = ""

def validate_regex(pattern):
    try:
        re.compile(pattern)
        return True, None
    except re.error as e:
        return False, str(e)

def convert_to_tenable_audit(json_data):
    audit_output = "<custom_item>\n"
    for key, value in json_data.items():
        padding = " " * (12 - len(key))
        formatted_value = f'"{value}"' if " " in str(value) else value
        audit_output += f"  {key}{padding} : {formatted_value}\n"
    audit_output += "</custom_item>"
    return audit_output

st.set_page_config(page_title="Tenable Audit Automator", layout="wide")
st.title("🛡️ Tenable Audit Automator")

# Sidebar
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if st.sidebar.button("Load IRS Banner Sample"):
    st.session_state.requirement_text = "[IRS Pub 1075] Section 9.3.1.1: System must display approved warning banner."

# Main UI
req_input = st.text_area("Compliance Requirement:", value=st.session_state.requirement_text, height=150)
col1, col2 = st.columns(2)
with col1:
    audit_type = st.selectbox("Item Type", ["FILE_CONTENT_CHECK", "BANNER_CHECK", "REGISTRY_SETTING"])
with col2:
    platform = st.selectbox("Platform", ["Unix", "Windows"])

if st.button("Generate .audit Item"):
    if not api_key:
        st.error("Please enter an API Key")
    else:
        client = OpenAI(api_key=api_key)
        prompt = f"Convert this to Tenable {audit_type} JSON: {req_input}. Use PCRE regex."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        res_json = json.loads(response.choices[0].message.content)
        st.code(convert_to_tenable_audit(res_json), language="xml")
