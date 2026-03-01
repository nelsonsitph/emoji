import streamlit as st
import pandas as pd
import requests

# 1. Page Configuration
st.set_page_config(page_title="Emoji Exporter", page_icon="🌟", layout="wide")
st.title("🌟 Professional Emoji Selection Tool")
st.markdown("Search, select, and export Unicode emojis for your materials.")

# 2. The Online Data Fetcher (Cached for speed)
@st.cache_data(show_spinner=False)
def fetch_emoji_data():
    # Using a fast, lightweight JSON source instead of the heavy HTML page
    url = "https://unpkg.com/emoji.json/emoji.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse the JSON directly
        data = response.json()
        
        emoji_list = []
        for item in data:
            # Format the data to match our table
            emoji_list.append({
                "Select": False, 
                "Emoji": item.get("char", ""),
                "Name": item.get("name", "").title(), # Capitalize the first letters
                "Unicode": "U+" + item.get("codes", "").replace(" ", " U+")
            })
            
        return pd.DataFrame(emoji_list)
        
    except Exception as e:
        st.error(f"Error fetching emoji data: {e}")
        return pd.DataFrame()

# 3. Load the data with a fast loading message
with st.spinner("Loading emojis... (This should only take a second!)"):
    df = fetch_emoji_data()

# 4. The User Interface
if not df.empty:
    # Search Bar
    search_query = st.text_input("🔍 Search emoji by name or keyword...", "")
    
    # Filter logic
    if search_query:
        filtered_df = df[df['Name'].str.contains(search_query, case=False, na=False)]
    else:
