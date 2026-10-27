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
    meal_date = st.date_input("දිනය (Date)", datetime.now())
    day_of_week = st.selectbox("දිනය (Day of the Week)", ["සඳුදා", "අඟහරුවාදා", "බදාදා", "බ්‍රහස්පතින්දා", "සිකුරාදා"])
    rice_type = st.selectbox("බත් වර්ගය (Rice Type)", ["සුදු බත්", "රතු බත්", "කහ බත්", "ෆ්‍රයිඩ් රයිස්"])
    main_dish = st.selectbox("ප්‍රධාන කෑම (Main Dish)", ["මාළු", "කුකුල් මස්", "බිත්තර", "කීරමින්", "හාල්මැස්සෝ", "කරවල"])
    
    # පරිප්පු හැමවෙලේම ඩිෆෝල්ට් එන නිසා, අනෙක් එළවළු වර්ගය පමණක් තෝරා ගැනීමට සැලසීම
    other_veggies = st.selectbox("අනෙකුත් එළවළු වර්ගය (Veggies)", ["බෝංචි", "කැරට්", "වට්ටක්කා", "රතුඅල", "පතෝල", "අඹ", "මුරුංගා", "අල", "වම්බටු", "කෙසෙල් මුව", "බටුමෝජු හාල්මැස්සො එකට", "කැකිරි", "කොහිල", "අල සහ කැරට් එකට", "අල තෙලට", "ග්‍රීන් පීස්", "දෙල්", "පොලොස්", "අළු කෙසෙල්", "ඇඹරැල්ල"])
    
    # පරිප්පු ස්වයංක්‍රීයව (Default) එළවළු සමඟ එකතු වීම
    if other_veggies != "-":
        veggies = f"පරිප්පු සමග {other_veggies}"
    else:
        veggies = "පරිප්පු පමණයි"
    
    greens = st.selectbox("කොළ වර්ග (Greens)", ["ගොටුකොළ", "මුකුණුවැන්න", "කන්කුන්", "කතුරුමුරුංගා", "ලූනු කොල", "සාරන", "එළවලු සලාද"])
    extras = st.text_input("අතිරේක (Extras)", "-")
    
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
                veggies,  # දැන් මෙතැනට උඩින් හැදුණු veggies විචල්‍යය (variable එක) ඇතුළත් වේ
                greens,
                extras if extras != "නැත" else "-"
            ]
            # Google Sheet එකට අලුත් පේළියක් ලෙස එකතු කිරීම
            sheet.append_row(row_data)
            
            st.success(f"🎉 {meal_date} ({day_of_week}) සඳහා කෑම විස්තර Google Sheet එකේ සාර්ථකව සටහන් කරගන්නා ලදී!")
            st.rerun()
        except Exception as e:
            st.error(f"දත්ත සේව් කිරීමේදී දෝෂයක් මතු විය: {e}")

st.markdown("---")
st.subheader("📅 මීට පෙර දුන් කෑම ලයිස්තුව (History)")
# ෂීට් එක ලෝඩ් කරගැනීම (මෙන්න මේක උඩින්ම තියෙන්න ඕන)
sheet = init_google_sheet()
# ගූගල් ෂීට් එකෙන් ඩේටා ලබා ගැනීම
data = sheet.get_all_records()

if data:
    df = pd.DataFrame(data)
    st.dataframe(df)
    
    st.markdown("---")
    st.markdown("### 🗑️ වැරදුණු දත්තයක් මකා දැමීම (Delete Entry)")
    
    # ෂීට් එකේ ඇති එක් එක් පේළිය සඳහා විස්තර ලැයිස්තුවක් සකස් කිරීම (Header එකත් සමඟ රෝ අංකය සලකා බැලේ)
    row_options = [f"Row {i+2}: දින: {row.get('meal_date', '')} | ප්‍රධාන කෑම: {row.get('main_dish', '')}" for i, row in enumerate(data)]
    
    selected_option = st.selectbox("මකා දැමිය යුතු දත්තය තෝරන්න:", row_options)
    
    if st.button("තෝරාගත් දත්තය මකන්න (Delete)"):
        if selected_option:
            # 'Row X' කියන එකෙන් අදාළ පේළි අංකය (Row Number) ලබා ගැනීම
            row_num = int(selected_option.split(":")[0].replace("Row ", ""))
            
            # Google Sheet එකෙන් අදාළ පේළිය මකා දැමීම
            sheet.delete_rows(row_num)
            
            st.success("දත්තය සාර්ථකව මකා දමන ලදී!")
            # ඇප් එක රිෆ්‍රෙශ් කිරීම සඳහා
            st.rerun()
else:
    st.info("තවම දත්ත ඇතුළත් කර නැත නැතහොත් ෂීට් එක හිස්ව ඇත.")


# Display saved data from Google Sheets
df_saved = load_data()
if not df_saved.empty:
    st.dataframe(df_saved, use_container_width=True)
else:
    st.info("තවම දත්ත ඇතුළත් කර නැත නැතහොත් ෂීට් එක හිස්ව ඇත.")