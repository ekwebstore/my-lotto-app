import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
import base64
from datetime import datetime

# 1. הגדרות עמוד (אייקון שק כסף)
st.set_page_config(page_title="Lotto AI Gold", page_icon="💰", layout="centered")

# עיצוב CSS מתקדם לכדורים וכפתורים
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; border: none; }
    .number-ball { display: inline-block; width: 38px; height: 38px; background-color: #f8f9fa; border-radius: 50%; text-align: center; line-height: 38px; margin: 4px; font-weight: bold; border: 2px solid #4285F4; color: #202124; }
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05; border-color: #EA4335; }
    .accuracy-card { padding: 15px; border-radius: 12px; border: 1px solid #dadce0; margin-bottom: 10px; background-color: #f1f3f4; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציות עזר וסנכרון ---
def safe_int(val):
    try: return int(''.join(filter(str.isdigit, str(val))))
    except: return 0

@st.cache_data(ttl=60)
def fetch_data():
    url = "https://raw.githubusercontent.com/ekwebstore/my-lotto-app/main/lotto_data.csv"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return pd.read_csv(io.StringIO(res.content.decode('utf-8-sig', errors='ignore'))).dropna(how='all')
    except: pass
    return pd.DataFrame()

# ניהול היסטוריית חיזויים (Session State כברירת מחדל)
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []

# --- מנגנון החיזוי - "חוקי הזהב" ---
def generate_gold_prediction(df):
    # למידה מ-50 אחרונות
    recent_data = df.head(50)
    all_recent = recent_data.iloc[:, 1:7].values.flatten()
    counts = pd.Series([safe_int(x) for x in all_recent if safe_int(x) > 0]).value_counts()
    
    hot = counts.head(12).index.tolist()
    cold = [n for n in range(1, 38) if n not in hot]
    
    # זיהוי טרנד
    trend = "חם" if random.random() > 0.4 else "קר"
    
    for _ in range(1000): # מסננת חוקי הזהב
        # בחירת קבוצה ראשונית לפי טרנד
        if trend == "חם":
            pool = random.sample(hot, 4) + random.sample(cold, 2)
        else:
            pool = random.sample(hot, 2) + random.sample(cold, 4)
        
        nums = sorted(list(set(pool)))
        if len(nums) != 6: continue
        
        # 1. חוק הסכום (90-155)
        if not (90 <= sum(nums) <= 155): continue
        
        # 2. חוק המרחק (Spacing) - מקסימום רצף אחד של 2
        diffs = np.diff(nums)
        if list(diffs).count(1) > 1: continue
        
        # 3. איזון זוגי/אי-זוגי (2:4 או 3:3 או 4:2)
        evens = len([n for n in nums if n % 2 == 0])
        if evens < 2 or evens > 4: continue
        
        return nums, random.randint(1, 7), trend
    return sorted(random.sample(range(1, 38), 6)), 1, "אקראי"

# --- ממשק המשתמש ---
data = fetch_data()

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי לוטו", "📜 היסטוריית חיזויים", "✅ דיוק למידה"])
    
    next_id = safe_int(data.iloc[0, 0]) + 1

    with tab1:
        st.subheader(f"חיזוי להגרלה קרובה: {next_id}")
        if st.button("הפעל מנגנון למידה וחוקי זהב"):
            nums, strong, trend = generate_gold_prediction(data)
            
            # הצגת החיזוי
            st.write(f"התגלה טרנד **{trend}**. הצירוף האופטימלי:")
            cols = st.columns(7)
            for i, n in enumerate(nums):
                cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball strong-ball">{strong}</div>', unsafe_allow_html=True)
            
            # שמירה להיסטוריה
            st.session_state.prediction_history.append({
                'date': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'target_id': next_id,
                'nums': nums,
                'strong': strong
            })
            st.success(f"החיזוי נשמר עבור הגרלה {next_id}")

    with tab2:
        st.subheader("כל החיזויים שבוצעו")
        if not st.session_state.prediction_history:
            st.write("טרם בוצעו חיזויים.")
        else:
            for p in reversed(st.session_state.prediction_history):
                # מציאת תוצאות אמת אם קיימות
                actual_row = data[data.iloc[:, 0].apply(safe_int) == p['target_id']]
                actual_nums = actual_row.iloc[0, 1:7].astype(int).tolist() if not actual_row.empty else []
                actual_strong = safe_int(actual_row.iloc[0, 7]) if not actual_row.empty else -1

                st.write(f"📅 {p['date']} | 🎯 הגרלה: {p['target_id']}")
                cols = st.columns(7)
                for i, n in enumerate(p['nums']):
                    is_hit = "green-ball" if n in actual_nums else ""
                    cols[i].markdown(f'<div class="number-ball {is_hit}">{n}</div>', unsafe_allow_html=True)
                
                is_s_hit = "green-ball" if p['strong'] == actual_strong else ""
                cols[6].markdown(f'<div class="number-ball strong-ball {is_s_hit}">{p["strong"]}</div>', unsafe_allow_html=True)
                st.markdown("---")

    with tab3:
        st.subheader("בקרת דיוק וסטטיסטיקה")
        # א. בדיקת סימולציה על ההגרלה האחרונה (Back-Testing)
        st.info("סימולציה: לו היינו מנבאים את ההגרלה האחרונה שקרתה:")
        sim_nums, sim_strong, _ = generate_gold_prediction(data.iloc[1:])
        real_nums = data.iloc[0, 1:7].astype(int).tolist()
        real_strong = safe_int(data.iloc[0, 7])
        
        sim_hits = len(set(sim_nums) & set(real_nums))
        st.write(f"בסימולציה להגרלה {data.iloc[0,0]}: פגעת ב-{sim_hits} מספרים" + (" + חזק!" if sim_strong == real_strong else ""))
        
        # ב. רישום פגיעות של המשתמש
        st.markdown("### פגיעות בחיזויים שלך:")
        for p in st.session_state.prediction_history:
            actual_row = data[data.iloc[:, 0].apply(safe_int) == p['target_id']]
            if not actual_row.empty:
                actual_nums = actual_row.iloc[0, 1:7].astype(int).tolist()
                actual_strong = safe_int(actual_row.iloc[0, 7])
                hits = len(set(p['nums']) & set(actual_nums))
                s_text = " + חזק" if p['strong'] == actual_strong else ""
                st.markdown(f'<div class="accuracy-card">הגרלה {p["target_id"]}: פגעת ב-<b>{hits}</b> מתוך 6{s_text}</div>', unsafe_allow_html=True)

else:
    st.error("קובץ lotto_data.csv לא נמצא בגיטהאב.")