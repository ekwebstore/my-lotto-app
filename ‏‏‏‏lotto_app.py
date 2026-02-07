import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
from datetime import datetime

# 1. הגדרות עמוד ואייקון (💰)
st.set_page_config(page_title="Lotto AI Pro", page_icon="💰", layout="centered")

# עיצוב CSS - המבנה המקורי והיציב שלך
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; border: none; }
    .number-ball { display: inline-block; width: 35px; height: 35px; background-color: #f8f9fa; border-radius: 50%; text-align: center; line-height: 35px; margin: 3px; font-weight: bold; border: 2px solid #4285F4; color: #202124; font-size: 14px; }
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05; border-color: #EA4335; }
    .accuracy-box { padding: 10px; background-color: #e8f0fe; border-radius: 10px; margin-bottom: 5px; border-right: 5px solid #4285F4; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# זיכרון פנימי
if 'my_predictions' not in st.session_state:
    st.session_state.my_predictions = []

def safe_int(val):
    try:
        if pd.isna(val): return 0
        clean_val = ''.join(filter(str.isdigit, str(val)))
        return int(clean_val) if clean_val else 0
    except: return 0

@st.cache_data(ttl=60)
def fetch_lotto_data():
    url = "https://raw.githubusercontent.com/ekwebstore/my-lotto-app/main/lotto_data.csv"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8-sig', errors='ignore')))
            return df.dropna(how='all')
        return pd.DataFrame()
    except: return pd.DataFrame()

def generate_prediction(df):
    """לוגיקת זהב משולבת - חכמה אך מהירה"""
    try:
        # למידה מ-50 הגרלות אחרונות בלבד (זיהוי טרנדים)
        recent_df = df.head(50)
        all_nums_raw = recent_df.iloc[:, 1:7].values.flatten()
        all_nums = [safe_int(n) for n in all_nums_raw if safe_int(n) > 0]
        
        if not all_nums: 
            return sorted(random.sample(range(1, 38), 6)), random.randint(1, 7)
            
        counts = pd.Series(all_nums).value_counts()
        hot = counts.head(15).index.tolist()
        cold = [n for n in range(1, 38) if n not in hot]
        
        for _ in range(300): # מוגבל ל-300 כדי למנוע קריסה
            # חוק הזהב 1: שילוב חם/קר
            pool = random.sample(hot, 4) + random.sample(cold, 2)
            nums = sorted(list(set(pool)))
            
            if len(nums) == 6:
                # חוק הזהב 2: טווח סכום אידיאלי
                if 90 <= sum(nums) <= 155:
                    # חוק הזהב 3: איזון זוגיות (2-4 זוגיים)
                    evens = len([n for n in nums if n % 2 == 0])
                    if 2 <= evens <= 4:
                        return nums, random.randint(1, 7)
    except: pass
    return sorted(random.sample(range(1, 38), 6)), random.randint(1, 7)

# --- ממשק ---
st.title("💰 Lotto AI Pro - Gold Edition")
data = fetch_lotto_data()

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי חדש", "📜 היסטוריה", "📊 דיוק"])
    
    next_id = safe_int(data.iloc[0, 0]) + 1

    with tab1:
        st.subheader(f"חיזוי להגרלה: {next_id}")
        if st.button("ייצר חיזוי זהב"):
            nums, strong = generate_prediction(data)
            st.session_state.my_predictions.append({
                'id': next_id, 'nums': nums, 'strong': strong, 
                'time': datetime.now().strftime("%H:%M:%S")
            })
            
            st.write("תוצאה:")
            cols = st.columns(7)
            for i, n in enumerate(nums):
                cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball strong-ball">{strong}</div>', unsafe_allow_html=True)
            st.success("החיזוי נבנה לפי חוקי הזהב ונשמר.")

    with tab2:
        if not st.session_state.my_predictions:
            st.info("אין נתונים.")
        else:
            for pred in reversed(st.session_state.my_predictions):
                actual_row = data[data.iloc[:, 0].apply(safe_int) == pred['id']]
                a_nums = [safe_int(actual_row.iloc[0, i]) for i in range(1, 7)] if not actual_row.empty else []
                a_strong = safe_int(actual_row.iloc[0, 7]) if not actual_row.empty else -1

                st.markdown(f"**הגרלה {pred['id']}** ({pred['time']})")
                cols = st.columns(7)
                for i, n in enumerate(pred['nums']):
                    hit = "green-ball" if n in a_nums else ""
                    cols[i].markdown(f'<div class="number-ball {hit}">{n}</div>', unsafe_allow_html=True)
                s_hit = "green-ball" if pred['strong'] == a_strong else ""
                cols[6].markdown(f'<div class="number-ball strong-ball {s_hit}">{pred["strong"]}</div>', unsafe_allow_html=True)
                st.write("---")

    with tab3:
        for pred in st.session_state.my_predictions:
            actual_row = data[data.iloc[:, 0].apply(safe_int) == pred['id']]
            if not actual_row.empty:
                a_nums = [safe_int(actual_row.iloc[0, i]) for i in range(1, 7)]
                hits = len(set(pred['nums']) & set(a_nums))
                st.markdown(f'<div class="accuracy-box">הגרלה {pred["id"]}: <b>{hits}</b> פגיעות</div>', unsafe_allow_html=True)
else:
    st.error("הקובץ לא נטען.")