import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
from datetime import datetime

# 1. הגדרות עמוד
st.set_page_config(page_title="Lotto AI Gold", page_icon="💰", layout="centered")

# עיצוב CSS - צפוף, פשוט וחסין למובייל
st.markdown("""
    <style>
    /* כפתור ירוק גדול */
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; }
    
    /* מכולה שמונעת ירידת שורה בנייד */
    .lotto-container {
        text-align: center;
        white-space: nowrap; /* מונע מהכדורים לרדת שורה */
        overflow-x: auto;    /* מאפשר גלילה לצדדים אם המסך ממש קטן */
        display: block;
        padding: 10px 0;
        width: 100%;
    }
    
    /* הכדור הצפוף והמקורי */
    .number-ball {
        display: inline-block;
        width: 34px;
        height: 34px;
        background-color: #f8f9fa;
        border-radius: 50%;
        text-align: center;
        line-height: 34px;
        margin: 2px; /* רווח מינימלי */
        font-weight: bold;
        border: 2px solid #4285F4;
        color: #202124;
        font-size: 14px;
    }
    
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05 !important; border-color: #EA4335 !important; }
    
    /* כרטיסיית פגיעות */
    .accuracy-card { padding: 10px; border-radius: 10px; border: 1px solid #dadce0; margin-bottom: 8px; background-color: #f1f3f4; direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציות עזר ---
def safe_int(val):
    try:
        if pd.isna(val): return 0
        s = ''.join(filter(str.isdigit, str(val)))
        return int(s) if s else 0
    except: return 0

def display_lotto_line(nums, strong, actual_nums=[], actual_strong=-1):
    """מציג את הכדורים בשורה אחת צפופה שאינה נשברת בנייד"""
    balls_html = '<div class="lotto-container">'
    for n in nums:
        is_hit = "green-ball" if n in actual_nums else ""
        balls_html += f'<div class="number-ball {is_hit}">{n}</div>'
    
    is_s_hit = "green-ball" if strong == actual_strong else ""
    balls_html += f'<div class="number-ball strong-ball {is_s_hit}">{strong}</div>'
    balls_html += '</div>'
    st.markdown(balls_html, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def fetch_data():
    url = "https://raw.githubusercontent.com/ekwebstore/my-lotto-app/main/lotto_data.csv"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            df = pd.read_csv(io.StringIO(res.content.decode('utf-8-sig', errors='ignore')))
            return df.dropna(how='all')
    except Exception as e:
        st.error(f"שגיאה בטעינה: {e}")
    return pd.DataFrame()

# אתחול היסטוריה
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []

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
                evens = len([n for n in nums if n % 2 == 0])
                if 2 <= evens <= 4:
                    return nums, random.randint(1, 7), trend
    return sorted(random.sample(range(1, 38), 6)), 1, "אקראי"

# --- ממשק האפליקציה ---
data = fetch_data()

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי", "📜 היסטוריה", "✅ דיוק"])
    next_id = safe_int(data.iloc[0, 0]) + 1

    with tab1:
        st.subheader(f"הגרלה {next_id}")
        if st.button("ייצר חיזוי זהב"):
            nums, strong, trend = generate_gold_prediction(data)
            display_lotto_line(nums, strong)
            st.session_state.prediction_history.append({
                'target_id': next_id, 
                'nums': nums, 
                'strong': strong, 
                'time': datetime.now().strftime("%H:%M")
            })
            st.caption(f"מבוסס על טרנד {trend}")

    with tab2:
        if not st.session_state.prediction_history:
            st.info("אין חיזויים שמורים.")
        else:
            for p in reversed(st.session_state.prediction_history):
                t_id = p.get('target_id', 0)
                actual_row = data[data.iloc[:, 0].apply(safe_int) == t_id]
                a_nums = [safe_int(x) for x in actual_row.iloc[0, 1:7]] if not actual_row.empty else []
                a_strong = safe_int(actual_row.iloc[0, 7]) if not actual_row.empty else -1
                
                st.write(f"🎯 הגרלה {t_id}")
                display_lotto_line(p['nums'], p['strong'], a_nums, a_strong)
                st.write("---")

    with tab3:
        if len(data) > 1:
            st.write(f"סימולציה על הגרלה {data.iloc[0,0]}:")
            sim_nums, sim_strong, _ = generate_gold_prediction(data.iloc[1:])
            real_nums = [safe_int(x) for x in data.iloc[0, 1:7]]
            real_strong = safe_int(data.iloc[0, 7])
            display_lotto_line(sim_nums, sim_strong, real_nums, real_strong)
            
            hits = len(set(sim_nums) & set(real_nums))
            st.write(f"המודל פגע ב-{hits} מספרים.")
else:
    st.error("לא ניתן לטעון נתונים מהשרת.")