import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
from datetime import datetime

# 1. הגדרות עמוד
st.set_page_config(page_title="Lotto AI Pro", page_icon="💰", layout="centered")

# עיצוב CSS - צמצום רווחים בלבד בלי לשנות מבנה
st.markdown("""
    <style>
    /* צמצום המרווח בין עמודות של Streamlit */
    [data-testid="column"] {
        padding: 0px 1px !important;
        flex: 1 1 auto !important;
        min-width: unset !important;
    }
    
    /* עיצוב כפתור */
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; border: none; }
    
    /* הכדור שלך */
    .number-ball { display: inline-block; width: 35px; height: 35px; background-color: #f8f9fa; border-radius: 50%; text-align: center; line-height: 35px; margin: 2px; font-weight: bold; border: 2px solid #4285F4; color: #202124; font-size: 14px; }
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05; border-color: #EA4335; }
    
    .accuracy-box { padding: 10px; background-color: #e8f0fe; border-radius: 10px; margin-bottom: 5px; border-right: 5px solid #4285F4; text-align: right; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

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
    except: pass
    return pd.DataFrame()

def generate_prediction(df):
    """חוקי הזהב מוטמעים כאן בצורה פשוטה שלא קורסת"""
    try:
        all_nums_raw = df.iloc[:50, 1:7].values.flatten()
        all_nums = [safe_int(n) for n in all_nums_raw if safe_int(n) > 0]
        counts = pd.Series(all_nums).value_counts()
        hot = counts.head(12).index.tolist()
        cold = [n for n in range(1, 38) if n not in hot]
        
        for _ in range(500):
            pool = random.sample(hot, 4) + random.sample(cold, 2)
            nums = sorted(list(set(pool)))
            if len(nums) == 6 and (90 <= sum(nums) <= 155):
                # בדיקת זוגיות - חוק הזהב השלישי
                evens = len([n for n in nums if n % 2 == 0])
                if 2 <= evens <= 4:
                    return nums, random.randint(1, 7)
    except: pass
    return sorted(random.sample(range(1, 38), 6)), random.randint(1, 7)

# --- גוף האפליקציה ---
st.title("💰 Lotto AI Pro")
data = fetch_lotto_data()

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי חדש", "📜 היסטוריה", "📊 דיוק"])
    next_id = safe_int(data.iloc[0, 0]) + 1

    with tab1:
        st.subheader(f"הגרלה: {next_id}")
        if st.button("ייצר חיזוי זהב"):
            nums, strong = generate_prediction(data)
            st.session_state.my_predictions.append({'id': next_id, 'nums': nums, 'strong': strong, 'time': datetime.now().strftime("%H:%M")})
            
            cols = st.columns(7)
            for i, n in enumerate(nums):
                cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball strong-ball">{strong}</div>', unsafe_allow_html=True)

    with tab2:
        if not st.session_state.my_predictions:
            st.info("אין חיזויים.")
        else:
            for pred in reversed(st.session_state.my_predictions):
                actual_row = data[data.iloc[:, 0].apply(safe_int) == pred['id']]
                a_nums = [safe_int(actual_row.iloc[0, i]) for i in range(1, 7)] if not actual_row.empty else []
                a_strong = safe_int(actual_row.iloc[0, 7]) if not actual_row.empty else -1
                
                st.write(f"🎯 הגרלה {pred['id']}")
                cols = st.columns(7)
                for i, n in enumerate(pred['nums']):
                    is_hit = "green-ball" if n in a_nums else ""
                    cols[i].markdown(f'<div class="number-ball {is_hit}">{n}</div>', unsafe_allow_html=True)
                is_s_hit = "green-ball" if pred['strong'] == a_strong else ""
                cols[6].markdown(f'<div class="number-ball strong-ball {is_s_hit}">{pred["strong"]}</div>', unsafe_allow_html=True)
                st.markdown("---")

    with tab3:
        for pred in st.session_state.my_predictions:
            actual_row = data[data.iloc[:, 0].apply(safe_int) == pred['id']]
            if not actual_row.empty:
                a_nums = [safe_int(actual_row.iloc[0, i]) for i in range(1, 7)]
                hits = len(set(pred['nums']) & set(a_nums))
                st.markdown(f'<div class="accuracy-box">הגרלה {pred["id"]}: {hits} פגיעות</div>', unsafe_allow_html=True)
else:
    st.error("הקובץ לא נטען.")