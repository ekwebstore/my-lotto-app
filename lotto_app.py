import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
from datetime import datetime

# 1. הגדרות עמוד ואייקון (💰)
st.set_page_config(page_title="Lotto AI Gold", page_icon="💰", layout="centered")

# עיצוב CSS מתקדם
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; border: none; }
    .number-ball { display: inline-block; width: 35px; height: 35px; background-color: #f8f9fa; border-radius: 50%; text-align: center; line-height: 35px; margin: 3px; font-weight: bold; border: 2px solid #4285F4; color: #202124; font-size: 14px; }
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05; border-color: #EA4335; }
    .history-card { padding: 12px; border-radius: 12px; border: 1px solid #dadce0; margin-bottom: 8px; background-color: #ffffff; direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציית משיכת נתונים מה-RAW GITHUB ---
@st.cache_data(ttl=60)
def fetch_lotto_data():
    # הקישור הישיר לקובץ שלך
    url = "https://raw.githubusercontent.com/ekwebstore/my-lotto-app/main/lotto_data.csv"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # שימוש ב-utf-8-sig כדי לטפל בסימני עברית אם ישנם
            content = response.content.decode('utf-8-sig', errors='ignore')
            df = pd.read_csv(io.StringIO(content))
            return df
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- לוגיקת חיזוי "חוקי הזהב" ---
def generate_prediction(df):
    try:
        # שליפת המספרים מהקובץ (מניח שהמספרים נמצאים בעמודות 1 עד 7)
        all_nums = df.iloc[:, 1:7].values.flatten()
        counts = pd.Series(all_nums).value_counts()
        hot = counts.head(12).index.tolist()
        cold = [n for n in range(1, 38) if n not in hot]
        
        for _ in range(500): # סימולציה למציאת הצירוף המושלם
            pool = random.sample(hot, 4) + random.sample(cold, 2) if random.random() > 0.5 else random.sample(hot, 2) + random.sample(cold, 4)
            nums = sorted(list(set(pool)))
            if len(nums) < 6: continue
            
            # בדיקת חוקי הזהב
            if 90 <= sum(nums) <= 155: # חוק הסכום
                diffs = np.diff(nums)
                if not (any(diffs == 1) and list(diffs).count(1) > 1): # חוק המרחק
                    evens = len([n for n in nums if n % 2 == 0])
                    if 2 <= evens <= 4: # חוק האיזון
                        return nums, random.randint(1, 7)
    except:
        pass
    return sorted(random.sample(range(1, 38), 6)), random.randint(1, 7)

# --- ממשק משתמש ---
st.title("💰 Lotto AI Pro")

data = fetch_lotto_data()

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי חדש", "📜 היסטוריה", "✅ דיוק למידה"])

    with tab1:
        st.subheader("הגרלה קרובה")
        st.write(f"הנתונים מבוססים על הגרלה אחרונה: **{data.iloc[0,0]}**")
        if st.button("ייצר חיזוי חוקי הזהב"):
            nums, strong = generate_prediction(data)
            cols = st.columns(7)
            for i, n in enumerate(nums):
                cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball strong-ball">{strong}</div>', unsafe_allow_html=True)
            st.balloons()

    with tab2:
        st.subheader("10 הגרלות אחרונות")
        for i in range(min(10, len(data))):
            row = data.iloc[i]
            st.markdown(f"""
            <div class="history-card">
                <strong>הגרלה {row[0]}</strong><br>
                {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}, {row[6]} | <b>חזק: {row[7]}</b>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader("בדיקת פגיעה (Backtest)")
        st.write("המערכת מנבאת את ההגרלה האחרונה בקובץ לצורך למידה:")
        
        test_data = data.iloc[1:] # לומד הכל חוץ מהחדשה ביותר
        actual = data.iloc[0]
        actual_nums = [int(actual[i]) for i in range(1, 7)]
        
        sim_nums, sim_strong = generate_prediction(test_data)
        
        cols = st.columns(7)
        for i, sn in enumerate(sim_nums):
            is_hit = "green-ball" if sn in actual_nums else ""
            cols[i].markdown(f'<div class="number-ball {is_hit}">{sn}</div>', unsafe_allow_html=True)
        
        is_s_hit = "green-ball" if sim_strong == int(actual[7]) else ""
        cols[6].markdown(f'<div class="number-ball strong-ball {is_s_hit}">{sim_strong}</div>', unsafe_allow_html=True)
        st.caption("ירוק = פגיעה בסימולציית הלמידה")

else:
    st.error("לא מצליח לגשת לקובץ. וודא שהמאגר בגיטהאב מוגדר כ-Public.")
    st.info("נתיב מבוקש: ekwebstore/my-lotto-app/main/lotto_data.csv")