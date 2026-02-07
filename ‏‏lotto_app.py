import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
from datetime import datetime

# 1. הגדרות עמוד (אייקון שק כסף)
st.set_page_config(page_title="Lotto AI Gold", page_icon="💰", layout="centered")

# --- עיצוב CSS מתקדם לתמיכה מלאה במובייל ---
st.markdown("""
    <style>
    /* עיצוב כפתור רחב וגדול לנייד */
    .stButton>button { 
        width: 100%; 
        border-radius: 25px; 
        background-color: #0F9D58; 
        color: white; 
        height: 3.5em; 
        font-weight: bold; 
        border: none;
        font-size: 18px;
    }
    
    /* מכולה ששומרת על הכדורים בשורה אחת מאוזנת */
    .lotto-row {
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        gap: 8px;
        margin: 15px 0;
        direction: ltr;
    }
    
    /* עיצוב כדור המספר */
    .ball {
        width: 38px;
        height: 38px;
        background-color: #f8f9fa;
        border-radius: 50%;
        text-align: center;
        line-height: 38px;
        font-weight: bold;
        border: 2px solid #4285F4;
        color: #202124;
        font-size: 15px;
        flex-shrink: 0; /* מונע מהכדור להתכווץ */
    }
    
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05 !important; border-color: #EA4335 !important; }
    
    /* כרטיסיית תוצאות */
    .accuracy-card { 
        padding: 12px; 
        border-radius: 12px; 
        border: 1px solid #dadce0; 
        margin-bottom: 10px; 
        background-color: #f1f3f4; 
        direction: rtl; 
        text-align: right; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציות עזר ---
def safe_int(val):
    try:
        if pd.isna(val): return 0
        s = ''.join(filter(str.isdigit, str(val)))
        return int(s) if s else 0
    except: return 0

def render_balls(nums, strong, actual_nums=[], actual_strong=-1):
    """פונקציה שמייצרת HTML של כדורים בשורה אחת מאוזנת"""
    html = '<div class="lotto-row">'
    for n in nums:
        hit_class = "green-ball" if n in actual_nums else ""
        html += f'<div class="ball {hit_class}">{n}</div>'
    
    s_hit_class = "green-ball" if strong == actual_strong else ""
    html += f'<div class="ball strong-ball {s_hit_class}">{strong}</div>'
    html += '</div>'
    return html

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

# --- טעינה ותצוגה ---
data = fetch_data()

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי", "📜 היסטוריה", "✅ דיוק"])
    next_id = safe_int(data.iloc[0, 0]) + 1

    with tab1:
        st.subheader(f"חיזוי להגרלה: {next_id}")
        if st.button("ייצר חיזוי חוקי הזהב"):
            nums, strong, trend = generate_gold_prediction(data)
            st.markdown(render_balls(nums, strong), unsafe_allow_html=True)
            st.session_state.prediction_history.append({
                'target_id': next_id, 'nums': nums, 'strong': strong, 'time': datetime.now().strftime("%H:%M")
            })
            st.caption(f"מבוסס על טרנד {trend} וניתוח 50 הגרלות אחרונות")

    with tab2:
        st.subheader("חיזויים שביצעת")
        if not st.session_state.prediction_history:
            st.info("בצע חיזוי כדי לראות תוצאות כאן.")
        else:
            for p in reversed(st.session_state.prediction_history):
                t_id = p.get('target_id', 0)
                actual_row = data[data.iloc[:, 0].apply(safe_int) == t_id]
                a_nums = [safe_int(x) for x in actual_row.iloc[0, 1:7]] if not actual_row.empty else []
                a_strong = safe_int(actual_row.iloc[0, 7]) if not actual_row.empty else -1
                
                st.write(f"🎯 הגרלה {t_id} | {p['time']}")
                st.markdown(render_balls(p['nums'], p['strong'], a_nums, a_strong), unsafe_allow_html=True)
                st.markdown("---")

    with tab3:
        st.subheader("בדיקת המודל")
        if len(data) > 1:
            st.write(f"סימולציה על הגרלה {data.iloc[0,0]}:")
            sim_nums, sim_strong, _ = generate_gold_prediction(data.iloc[1:])
            real_nums = [safe_int(x) for x in data.iloc[0, 1:7]]
            real_strong = safe_int(data.iloc[0, 7])
            st.markdown(render_balls(sim_nums, sim_strong, real_nums, real_strong), unsafe_allow_html=True)
            hits = len(set(sim_nums) & set(real_nums))
            st.info(f"המודל פגע ב-{hits} מספרים בסימולציה.")
        
        for p in st.session_state.prediction_history:
            actual_row = data[data.iloc[:, 0].apply(safe_int) == p['target_id']]
            if not actual_row.empty:
                actual_nums = [safe_int(x) for x in actual_row.iloc[0, 1:7]]
                hits = len(set(p['nums']) & set(actual_nums))
                st.markdown(f'<div class="accuracy-card">הגרלה {p["target_id"]}: <b>{hits}</b> פגיעות</div>', unsafe_allow_html=True)
else:
    st.error("קובץ הנתונים לא נטען.")