import streamlit as st
import pandas as pd
import requests

# 1. Page Configuration
st.set_page_config(page_title="Emoji Exporter", page_icon="🌟", layout="wide")

st.title("🌟 Professional Emoji Selection Tool")
st.markdown("Search, select, and build your list of Unicode emojis across multiple searches.")

# Quick Jump Button
st.markdown("""
    <style>
    .jump-btn {
        background-color: #007bff;
        color: white !important;
        padding: 8px 16px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }
    .jump-btn:hover { background-color: #0056b3; }
    </style>
    <a href="#export-section" class="jump-btn">⬇️ Jump Down to Export Cart</a>
""", unsafe_allow_html=True)

# Initialize a "shopping cart" in the session state
if 'selection_cart' not in st.session_state:
    st.session_state.selection_cart = {}

# 2. The Online Data Fetcher (Cached for speed)
@st.cache_data(show_spinner=False)
def fetch_emoji_data():
    url = "https://unpkg.com/emoji.json/emoji.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        emoji_list = []
        for item in data:
            emoji_list.append({
                "Emoji": item.get("char", ""),
                "Name": item.get("name", "").title(),
                "Unicode": "U+" + item.get("codes", "").replace(" ", " U+")
            })
        return pd.DataFrame(emoji_list)
    except Exception as e:
        st.error(f"Error fetching emoji data: {e}")
        return pd.DataFrame()

# 3. Load the data
with st.spinner("Loading emojis..."):
    df = fetch_emoji_data()

# 4. The User Interface
if not df.empty:
    search_query = st.text_input("🔍 Search emoji by name or keyword...", "")
    
    if search_query:
        filtered_df = df[df['Name'].str.contains(search_query, case=False, na=False)].copy()
    else:
        filtered_df = df.copy()

    # Pre-check boxes if the emoji is already in our shopping cart
    filtered_df.insert(0, "Select", filtered_df['Unicode'].isin(st.session_state.selection_cart.keys()))

    st.write(f"Showing **{len(filtered_df)}** emojis matching your search")

    # --- DYNAMIC HEIGHT UPGRADE ---
    # The table will calculate its own height based on the number of results.
    # It allows 35 pixels per row, capped at a maximum of 800 pixels tall so it doesn't break your page.
    table_height = min(len(filtered_df) * 35 + 45, 800)

    # Interactive Data Table
    edited_df = st.data_editor(
        filtered_df,
        column_config={
            "Select": st.column_config.CheckboxColumn("Add to Export", default=False),
            "Emoji": st.column_config.TextColumn("Emoji", width="small"),
            "Name": st.column_config.TextColumn("Description", width="large"),
            "Unicode": st.column_config.TextColumn("Unicode", width="medium"),
        },
        disabled=["Emoji", "Name", "Unicode"], 
        hide_index=True,
        use_container_width=True,
        height=table_height,  # <-- Using our new smart height calculation
        key="emoji_table" 
    )

    # Update the shopping cart
    for index, row in edited_df.iterrows():
        u = row['Unicode']
        if row['Select']:
            if u not in st.session_state.selection_cart:
                st.session_state.selection_cart[u] = {
                    "Emoji": row['Emoji'],
                    "Name": row['Name'],
                    "Unicode": u
                }
        else:
            if u in st.session_state.selection_cart:
                del st.session_state.selection_cart[u]

    # 5. Export Logic
    st.markdown("<div id='export-section'></div>", unsafe_allow_html=True) 
    st.markdown("---")
    
    st.subheader(f"🛒 Your Export Cart: {len(st.session_state.selection_cart)} emojis selected")
    
    if len(st.session_state.selection_cart) > 0:
        export_df = pd.DataFrame(list(st.session_state.selection_cart.values()))
        
        st.dataframe(export_df, hide_index=True, use_container_width=True, height=250)
        
        csv_data = export_df.to_csv(index=False).encode('utf-8-sig')
        
        col1, col2 = st.columns([1, 4])
        with col1:
            st.download_button(
                label="📥 Download CSV File",
                data=csv_data,
                file_name="selected_emojis.csv",
                mime="text/csv",
                type="primary"
            )
        with col2:
            if st.button("🗑️ Clear Cart"):
                st.session_state.selection_cart = {}
                st.rerun() 
    else:
        st.info("Search above and check the boxes. Your selections will appear here!")