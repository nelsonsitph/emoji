import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="Emoji Exporter", page_icon="🌟", layout="wide")
st.title("🌟 Professional Emoji Selection Tool")
st.markdown("Search, select, and export Unicode emojis for your educational materials.")

# 2. The Online Scraper (Cached for speed)
@st.cache_data(show_spinner=False) # Hide default spinner, we'll make a custom one
def fetch_emoji_data():
    url = "https://unicode.org/emoji/charts/full-emoji-list.html"
    
    try:
        # Fetch the HTML directly from Unicode
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        emoji_list = []
        # Parse the giant table
        for row in soup.find_all('tr'):
            chars = row.find('td', class_='chars')
            name = row.find('td', class_='name')
            code = row.find('td', class_='code')
            
            if chars and name and code:
                emoji_list.append({
                    "Select": False, # Default checkbox state
                    "Emoji": chars.text.strip(),
                    "Name": name.text.strip(),
                    "Unicode": code.text.strip()
                })
        
        # Convert to a Pandas DataFrame
        return pd.DataFrame(emoji_list)
        
    except Exception as e:
        st.error(f"Error fetching data from Unicode: {e}")
        return pd.DataFrame()

# 3. Load the data with a friendly loading message
with st.spinner("Downloading the latest 3,000+ emojis from Unicode... (This takes about 10-20 seconds on the first load)"):
    df = fetch_emoji_data()

# 4. The User Interface
if not df.empty:
    # Search Bar
    search_query = st.text_input("🔍 Search emoji by name or keyword...", "")
    
    # Filter logic
    if search_query:
        filtered_df = df[df['Name'].str.contains(search_query, case=False, na=False)]
    else:
        filtered_df = df

    st.write(f"Showing **{len(filtered_df)}** emojis")

    # Interactive Data Table
    edited_df = st.data_editor(
        filtered_df,
        column_config={
            "Select": st.column_config.CheckboxColumn("Add to Export", default=False),
            "Emoji": st.column_config.TextColumn("Emoji", width="small"),
            "Name": st.column_config.TextColumn("Description", width="large"),
            "Unicode": st.column_config.TextColumn("Unicode", width="medium"),
        },
        disabled=["Emoji", "Name", "Unicode"], # Prevent colleagues from editing the actual text
        hide_index=True,
        use_container_width=True,
        height=500
    )

    # 5. Export Logic
    selected_rows = edited_df[edited_df["Select"] == True]

    st.markdown("---")
    st.subheader("📥 Export Selected Emojis")
    
    if not selected_rows.empty:
        st.success(f"You have selected {len(selected_rows)} emojis.")
        
        # Prepare the final CSV format
        export_df = selected_rows.drop(columns=["Select"])
        csv_data = export_df.to_csv(index=False).encode('utf-8-sig') # utf-8-sig is crucial for Excel
        
        st.download_button(
            label="Download Excel (CSV) File",
            data=csv_data,
            file_name="selected_emojis.csv",
            mime="text/csv",
            type="primary"
        )
    else:
        st.info("Check the boxes next to the emojis above to export them.")
