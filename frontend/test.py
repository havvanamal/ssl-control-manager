import streamlit as st
import requests

st.title("SSL Manager - Test")

API_URL = "http://localhost:8000"

st.write(f"API URL: {API_URL}")

if st.button("Test API"):
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        st.success(f"Başarılı! Status: {response.status_code}")
        st.json(response.json())
    except Exception as e:
        st.error(f"Hata: {e}")

if st.button("Get Certificates"):
    try:
        response = requests.get(f"{API_URL}/api/certificates", timeout=5)
        st.success(f"Status: {response.status_code}")
        st.json(response.json())
    except Exception as e:
        st.error(f"Hata: {e}")