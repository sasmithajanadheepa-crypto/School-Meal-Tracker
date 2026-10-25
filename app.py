import json
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="අම්මාගේ පාසල් කෑම සටහන", page_icon="🍚", layout="centered")

st.title("🍚 පාසල් කෑම සැපයුම් කළමනාකරණ පද්ධතිය")
st.write("අම්මාට දිනපතා දෙන කෑම වේල් පහසුවෙන් සටහන් කර තබා ගැනීමට සහ පරීක්ෂා කිරීමට මෙම යෙදුම භාවිතා කරන්න.")

# Google Sheets Connection Setup
@st.cache_resource
def init_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

    client = gspread.authorize(creds)
    sheet = client.open("School Meal Tracker Data").sheet1
    return sheet

# Function to load existing data from Google Sheets
def load_data():
    try:
        sheet = init_google_sheet()
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
        else:
            return pd.DataFrame(columns=["meal_date", "day_of_week", "rice_type", "main_dish", "veggies", "greens", "extras"])
    except Exception as e:
        st.error(st.error(f"දත්ත ලබාගැනීමේ දෝෂයක් මතු විය: {e}"))
        return pd.DataFrame(columns=["meal_date", "day_of_week", "rice_type", "main_dish", "veggies", "greens", "extras"])

# Input Form with Dropdowns
with st.form("meal_form"):
    st.subheader("📝 නව දවසේ කෑම විස්තර ඇතුළත් කරන්න")
    
    col1, col2 = st.columns(2)
    with col1:
        meal_date = st.date_input("දිනය (Date)", datetime.now())
    with col2:
        day_of_week = st.selectbox("සතියේ දවස", ["සඳුදා", "අඟහරුවාදා", "බදාදා", "බ්‍රහස්පතින්දා", "සිකුරාදා"])
        
    # Drop-down options
    rice_options = ["සුදු බත්", "රතු බත්", "ෆ්‍රයිඩ් රයිස්", "කහ බත්", "වෙනත්"]
    main_dish_options = ["මාළු", "මස්", "බිත්තර", "හාල්මැස්සෝ", "කීරමින්", "කරවල", "වෙනත්"]
    veggie_options = ["පරිප්පු", "රතු අල", "කොහිල", "කැකිරි", "අල සහ කැරට් එකට", "අළු කෙසෙල්", "දෙල්", "ලූනු කොළ", "වෙනත්"]
    greens_options = ["ගොටුකොළ", "කන්කුන්", "මුකුණුවැන්න", "කතුරුමුරුංගා", "වෙනත්"]
    dessert_options = ["නැත", "කෙසෙල්", "ගස්ලබු", "කොමඩු", "චොකලට්", "පේර", "වෙනත්"]

    col3, col4 = st.columns(2)
    with col3:
        rice_type = st.selectbox("බත් වර්ගය", rice_options)
        if rice_type == "වෙනත්":
            rice_type = st.text_input("වෙනත් බත් වර්ගය සඳහන් කරන්න")
            
        main_dish = st.selectbox("ප්‍රධාන ව්‍යාංජනය", main_dish_options)
        if main_dish == "වෙනත්":
            main_dish = st.text_input("වෙනත් ප්‍රධාන ව්‍යාංජනය සඳහන් කරන්න")
            
        veggies = st.selectbox("එළවළු", veggie_options)
        if veggies == "වෙනත්":
            veggies = st.text_input("වෙනත් එළවළු සඳහන් කරන්න")
            
    with col4:
        greens = st.selectbox("කොළ වර්ගය", greens_options)
        if greens == "වෙනත්":
            greens = st.text_input("වෙනත් කොළ වර්ගයක් සඳහන් කරන්න")
            
        extras = st.selectbox("අතුරුපස / අමතර", dessert_options)
        if extras == "වෙනත්":
            extras = st.text_input("වෙනත් අතුරුපසක් සඳහන් කරන්න")
    
    submitted = st.form_submit_button("සටහන් කරගන්න (Save)")
    
    if submitted:
        try:
            sheet = init_google_sheet()
            # නව පේළියට අදාළ දත්ත ලැයිස්තුව සැකසීම
            row_data = [
                str(meal_date),
                day_of_week,
                rice_type,
                main_dish,
                veggies,
                greens,
                extras if extras != "නැත" else "-"
            ]
            # Google Sheet එකට අලුත් පේළියක් ලෙස එකතු කිරීම
            sheet.append_row(row_data)
            
            st.success(f"🎉 {meal_date} ({day_of_week}) සඳහා කෑම විස්තර Google Sheet එකේ සාර්ථකව සටහන් කරගන්නා ලදී!")
        except Exception as e:
            st.error(f"දත්ත සේව් කිරීමේදී දෝෂයක් මතු විය: {e}")

st.markdown("---")
st.subheader("📅 මීට පෙර දුන් කෑම ලැයිස්තුව (History)")

# Display saved data from Google Sheets
df_saved = load_data()
if not df_saved.empty:
    st.dataframe(df_saved, use_container_width=True)
else:
    st.info("තවම දත්ත ඇතුළත් කර නැත නැතහොත් ෂීට් එක හිස්ව ඇත.")
        