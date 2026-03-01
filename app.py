import streamlit as st
import pandas as pd
import requests

# 1. Page Configuration
st.set_page_config(page_title="Emoji Exporter", page_icon="🌟", layout="wide")
st.title("🌟 Professional Emoji Selection Tool")
st.markdown("Search, select, and build your list of Unicode emojis across multiple searches.")

# Initialize a "shopping cart" in the session state to remember picks permanently
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
with st.spinner("Loading emojis... (This should only take a second!)"):
    df = fetch_emoji_data()

# 4. The User Interface
if not df.empty:
    # Search Bar
    search_query = st.text_input("🔍 Search emoji by name or keyword...", "")
    
    # Filter logic
    if search_query:
        # Create a copy so we don't modify the original cached dataframe
        filtered_df = df[df['Name'].str.contains(search_query, case=False, na=False)].copy()
    else:
        filtered_df = df.copy()

    # Pre-check boxes if the emoji is already in our shopping cart
    filtered_df.insert(0, "Select", filtered_df['Unicode'].isin(st.session_state.selection_cart.keys()))

    st.write(f"Showing **{len(filtered_df)}** emojis matching your search")

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
        height=400,
        key="emoji_table" # Helps Streamlit track the table smoothly
    )

    # Update the shopping cart based on what the user checked/unchecked in the current view
    for index, row in edited_df.iterrows():
        u = row['Unicode']
        if row['Select']:
            # If checked, add to cart
            if u not in st.session_state.selection_cart:
                st.session_state.selection_cart[u] = {
                    "Emoji": row['Emoji'],
                    "Name": row['Name'],
                    "Unicode": u
                }
        else:
            # If unchecked, remove from cart
            if u in st.session_state.selection_cart:
                del st.session_state.selection_cart[u]

    # 5. Export Logic (Based entirely on the Cart, not just the search results)
    st.markdown("---")
    st.subheader(f"🛒 Your Export Cart: {len(st.session_state.selection_cart)} emojis selected")
    
    if len(st.session_state.selection_cart) > 0:
        # Convert the cart dictionary back into a Dataframe for export
        export_df = pd.DataFrame(list(st.session_state.selection_cart.values()))
        
        # Show a mini-preview of everything they have picked so far
        st.dataframe(export_df, hide_index=True, use_container_width=True)
        
        csv_data = export_df.to_csv(index=False).encode('utf-8-sig')
        
        # Layout buttons side-by-side
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
            # Add a handy button to clear the cart and start over
            if st.button("🗑️ Clear Cart"):
                st.session_state.selection_cart = {}
                st.rerun() # Refresh the page instantly
    else:
        st.info("Search above and check the boxes. Your selections will appear here!")