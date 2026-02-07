import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
from datetime import datetime

# 1. הגדרות עמוד
st.set_page_config(page_title="Lotto AI Gold", page_icon="💰", layout="centered")

# עיצוב CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; border: none; }
    .number-ball { display: inline-block; width: 35px; height: 35px; background-color: #f8f9fa; border-radius: 50%; text-align: center; line-height: 35px; margin: 3px; font-weight: bold; border: 2px solid #4285F4; color: #202124; font-size: 14px; }
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05; border-color: #EA4335; }
    .accuracy-card { padding: 12px; border-radius: 12px; border: 1px solid #dadce0; margin-bottom: 10px; background-color: #f1f3f4; direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציות עזר ---
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

# ניהול היסטוריה בזיכרון המערכת - עם הגנה משגיאות מבנה
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []

# --- מנגנון חוקי הזהב ---
def generate_gold_prediction(df):
    if df.empty: return sorted(random.sample(range(1, 38), 6)), 1, "אקראי"
    all_recent = df.head(50).iloc[:, 1:7].values.flatten()
    nums_list = [safe_int(x) for x in all_recent if safe_int(x) > 0]
    counts = pd.Series(nums_list).value_counts()
    hot = counts.head(12).index.tolist()
    cold = [n for n in range(1, 38) if n not in hot]
    
    trend = "חם" if random.random() > 0.4 else "קר"
    for _ in range(1000):
        pool = random.sample(hot, 4) + random.sample(cold, 2) if trend == "חם" else random.sample(hot, 2) + random.sample(cold, 4)
        nums = sorted(list(set(pool)))
        if len(nums) == 6 and (90 <= sum(nums) <= 155):
            if list(np.diff(nums)).count(1) <= 1:
                if 2 <= len([n for n in nums if n % 2 == 0]) <= 4:
                    return nums, random.randint(1, 7), trend
    return sorted(random.sample(range(1, 38), 6)), 1, "אקראי"

# --- טעינת נתונים ---
data = fetch_data()

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי לוטו", "📜 היסטוריית חיזויים", "✅ דיוק למידה"])
    
    # זיהוי הגרלה באה
    last_id = safe_int(data.iloc[0, 0])
    next_id = last_id + 1

    with tab1:
        st.subheader(f"חיזוי להגרלה מספר: {next_id}")
        if st.button("ייצר חיזוי חכם"):
            nums, strong, trend = generate_gold_prediction(data)
            cols = st.columns(7)
            for i, n in enumerate(nums):
                cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball strong-ball">{strong}</div>', unsafe_allow_html=True)
            
            # שימוש במפתח אחיד target_id למניעת KeyError
            st.session_state.prediction_history.append({
                'target_id': next_id, 
                'nums': nums, 
                'strong': strong, 
                'time': datetime.now().strftime("%H:%M")
            })
            st.success("החיזוי נשמר בהיסטוריה זמנית")

    with tab2:
        st.subheader("חיזויים שבוצעו במפגש זה")
        if not st.session_state.prediction_history:
            st.info("טרם בוצעו חיזויים.")
        else:
            for p in reversed(st.session_state.prediction_history):
                # שליפת נתונים בטוחה עם get() למניעת קריסה
                t_id = p.get('target_id', 0)
                p_nums = p.get('nums', [])
                p_strong = p.get('strong', 0)

                actual_row = data[data.iloc[:, 0].apply(safe_int) == t_id]
                actual_nums = [safe_int(x) for x in actual_row.iloc[0, 1:7]] if not actual_row.empty else []
                actual_strong = safe_int(actual_row.iloc[0, 7]) if not actual_row.empty else -1

                st.write(f"🎯 **הגרלה {t_id}** | בוצע ב-{p.get('time', 'Unknown')}")
                cols = st.columns(7)
                for i, n in enumerate(p_nums):
                    is_hit = "green-ball" if n in actual_nums else ""
                    cols[i].markdown(f'<div class="number-ball {is_hit}">{n}</div>', unsafe_allow_html=True)
                
                is_s_hit = "green-ball" if p_strong == actual_strong else ""
                cols[6].markdown(f'<div class="number-ball strong-ball {is_s_hit}">{p_strong}</div>', unsafe_allow_html=True)
                st.markdown("---")

    with tab3:
        st.subheader("בקרת דיוק")
        # סימולציה על ההגרלה הכי חדשה בקובץ
        if len(data) > 1:
            st.info(f"בדיקת מודל על תוצאות אמת (הגרלה {data.iloc[0,0]}):")
            sim_nums, sim_strong, _ = generate_gold_prediction(data.iloc[1:])
            real_nums = [safe_int(x) for x in data.iloc[0, 1:7]]
            hits = len(set(sim_nums) & set(real_nums))
            st.write(f"האלגוריתם זיהה **{hits}** מספרים נכונים בבדיקה זו.")
            st.markdown("---")
        
        for p in st.session_state.prediction_history:
            t_id = p.get('target_id', 0)
            actual_row = data[data.iloc[:, 0].apply(safe_int) == t_id]
            if not actual_row.empty:
                actual_nums = [safe_int(x) for x in actual_row.iloc[0, 1:7]]
                hits = len(set(p.get('nums', [])) & set(actual_nums))
                st.markdown(f'<div class="accuracy-card">הגרלה {t_id}: <b>{hits}</b> פגיעות נכונות</div>', unsafe_allow_html=True)
            else:
                st.write(f"הגרלה {t_id}: טרם פורסמו תוצאות אמת.")
else:
    st.error("שגיאה בטעינת הנתונים מ-GitHub.")