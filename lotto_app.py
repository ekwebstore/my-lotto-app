import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
from datetime import datetime

# 1. הגדרות עמוד ואייקון (💰)
st.set_page_config(page_title="Lotto AI Pro", page_icon="💰", layout="centered")

# עיצוב CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; border: none; }
    .number-ball { display: inline-block; width: 35px; height: 35px; background-color: #f8f9fa; border-radius: 50%; text-align: center; line-height: 35px; margin: 3px; font-weight: bold; border: 2px solid #4285F4; color: #202124; font-size: 14px; }
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05; border-color: #EA4335; }
    .history-card { padding: 12px; border-radius: 12px; border: 1px solid #dadce0; margin-bottom: 8px; background-color: #ffffff; direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה להמרת ערך למספר בצורה בטוחה
def safe_int(val):
    try:
        if pd.isna(val): return 0
        # ניקוי תווים לא מספריים למקרה שיש רווחים או פסיקים
        clean_val = ''.join(filter(str.isdigit, str(val)))
        return int(clean_val) if clean_val else 0
    except:
        return 0

@st.cache_data(ttl=60)
def fetch_lotto_data():
    url = "https://raw.githubusercontent.com/ekwebstore/my-lotto-app/main/lotto_data.csv"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.content.decode('utf-8-sig', errors='ignore')
            df = pd.read_csv(io.StringIO(content))
            # ניקוי שורות ריקות לחלוטין
            df = df.dropna(how='all')
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

def generate_prediction(df):
    try:
        # חילוץ והמרה בטוחה של מספרים
        all_nums_raw = df.iloc[:, 1:7].values.flatten()
        all_nums = [safe_int(n) for n in all_nums_raw if safe_int(n) > 0]
        
        if not all_nums: return sorted(random.sample(range(1, 38), 6)), random.randint(1, 7)
        
        counts = pd.Series(all_nums).value_counts()
        hot = counts.head(12).index.tolist()
        cold = [n for n in range(1, 38) if n not in hot]
        
        for _ in range(500):
            pool = random.sample(hot, 4) + random.sample(cold, 2) if random.random() > 0.5 else random.sample(hot, 2) + random.sample(cold, 4)
            nums = sorted(list(set(pool)))
            if len(nums) < 6: continue
            
            if 90 <= sum(nums) <= 155:
                diffs = np.diff(nums)
                if not (any(diffs == 1) and list(diffs).count(1) > 1):
                    evens = len([n for n in nums if n % 2 == 0])
                    if 2 <= evens <= 4:
                        return nums, random.randint(1, 7)
    except:
        pass
    return sorted(random.sample(range(1, 38), 6)), random.randint(1, 7)

st.title("💰 Lotto AI Pro")
data = fetch_lotto_data()

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי חדש", "📜 היסטוריה", "✅ דיוק למידה"])

    with tab1:
        st.subheader("הגרלה קרובה")
        if st.button("ייצר חיזוי חוקי הזהב"):
            nums, strong = generate_prediction(data)
            cols = st.columns(7)
            for i, n in enumerate(nums):
                cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball strong-ball">{strong}</div>', unsafe_allow_html=True)
            st.balloons()

    with tab2:
        st.subheader("הגרלות אחרונות")
        for i in range(min(10, len(data))):
            row = data.iloc[i]
            # מציג רק אם יש נתונים בשורה
            if not pd.isna(row[0]):
                st.markdown(f"""
                <div class="history-card">
                    <strong>הגרלה {row[0]}</strong><br>
                    {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}, {row[6]} | <b>חזק: {row[7]}</b>
                </div>
                """, unsafe_allow_html=True)

    with tab3:
        st.subheader("בדיקת פגיעה (Backtest)")
        if len(data) > 1:
            test_data = data.iloc[1:]
            actual = data.iloc[0]
            # שימוש בפונקציית המרה בטוחה
            actual_nums = [safe_int(actual[i]) for i in range(1, 7)]
            actual_strong = safe_int(actual[7])
            
            sim_nums, sim_strong = generate_prediction(test_data)
            
            cols = st.columns(7)
            for i, sn in enumerate(sim_nums):
                is_hit = "green-ball" if sn in actual_nums and sn > 0 else ""
                cols[i].markdown(f'<div class="number-ball {is_hit}">{sn}</div>', unsafe_allow_html=True)
            
            is_s_hit = "green-ball" if sim_strong == actual_strong and sim_strong > 0 else ""
            cols[6].markdown(f'<div class="number-ball strong-ball {is_s_hit}">{sim_strong}</div>', unsafe_allow_html=True)

else:
    st.error("לא מצליח לגשת לנתונים. וודא שקובץ ה-CSV תקין ובפורמט הנכון.")