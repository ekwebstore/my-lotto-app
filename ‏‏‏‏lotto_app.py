import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
from datetime import datetime

st.set_page_config(page_title="Lotto AI Gold", page_icon="💰", layout="centered")

# עיצוב CSS מתוקן לצפיפות עמודות
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; border: none; }
    
    /* עיצוב הכדור */
    .number-ball { display: inline-block; width: 35px; height: 35px; background-color: #f8f9fa; border-radius: 50%; text-align: center; line-height: 35px; font-weight: bold; border: 2px solid #4285F4; color: #202124; font-size: 14px; }
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05; border-color: #EA4335; }
    
    /* התיקון לעמודות - כאן קורה הקסם */
    [data-testid="column"] {
        width: fit-content !important;
        flex: unset !important;
        min-width: unset !important;
        padding: 0px 1px !important; /* רווח של 1 פיקסל בלבד בין עמודה לעמודה */
    }
    [data-testid="stHorizontalBlock"] {
        justify-content: center !important;
        gap: 0px !important;
    }
    
    .accuracy-card { padding: 12px; border-radius: 12px; border: 1px solid #dadce0; margin-bottom: 10px; background-color: #f1f3f4; direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציות לוגיקה (חוקי הזהב שלך) ---
def safe_int(val):
    try:
        if pd.isna(val): return 0
        s = ''.join(filter(str.isdigit, str(val)))
        return int(s) if s else 0
    except: return 0

@st.cache_data(ttl=60)
def fetch_data():
    url = "https://raw.githubusercontent.com/ekwebstore/my-lotto-app/main/lotto_data.csv"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            df = pd.read_csv(io.StringIO(res.content.decode('utf-8-sig', errors='ignore')))
            return df.dropna(how='all')
    except: pass
    return pd.DataFrame()

def generate_gold_prediction(df):
    if df.empty: return sorted(random.sample(range(1, 38), 6)), 1
    all_recent = df.head(50).iloc[:, 1:7].values.flatten()
    nums_list = [safe_int(x) for x in all_recent if safe_int(x) > 0]
    counts = pd.Series(nums_list).value_counts()
    hot = counts.head(12).index.tolist()
    cold = [n for n in range(1, 38) if n not in hot]
    
    for _ in range(500):
        pool = random.sample(hot, 4) + random.sample(cold, 2)
        nums = sorted(list(set(pool)))
        if len(nums) == 6 and (90 <= sum(nums) <= 155):
            if list(np.diff(nums)).count(1) <= 1:
                if 2 <= len([n for n in nums if n % 2 == 0]) <= 4:
                    return nums, random.randint(1, 7)
    return sorted(random.sample(range(1, 38), 6)), 1

# --- ממשק ---
data = fetch_data()

if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי", "📜 היסטוריה", "✅ דיוק"])
    next_id = safe_int(data.iloc[0, 0]) + 1

    with tab1:
        st.subheader(f"הגרלה {next_id}")
        if st.button("ייצר חיזוי חכם"):
            nums, strong = generate_gold_prediction(data)
            cols = st.columns(7)
            for i, n in enumerate(nums):
                cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball strong-ball">{strong}</div>', unsafe_allow_html=True)
            
            st.session_state.prediction_history.append({
                'target_id': next_id, 'nums': nums, 'strong': strong, 'time': datetime.now().strftime("%H:%M")
            })

    with tab2:
        for p in reversed(st.session_state.prediction_history):
            st.write(f"🎯 הגרלה {p['target_id']}")
            cols = st.columns(7)
            for i, n in enumerate(p['nums']):
                cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball strong-ball">{p["strong"]}</div>', unsafe_allow_html=True)
            st.write("---")

    with tab3:
        st.info("כאן מופיעה בקרת הדיוק על בסיס חוקי הזהב.")
else:
    st.error("שגיאה בטעינה.")