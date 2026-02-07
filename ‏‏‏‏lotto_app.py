import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
from datetime import datetime

# 1. הגדרות עמוד
st.set_page_config(page_title="Lotto AI Gold", page_icon="💰", layout="centered")

# עיצוב CSS - צמצום רווחים מקסימלי
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; }
    
    /* מכולה ששומרת על הכדורים בשורה אחת */
    .ball-container {
        display: flex;
        justify-content: center;
        gap: 5px; /* המרווח בין הכדורים - ניתן לשינוי */
        margin: 10px 0;
        direction: ltr;
        flex-wrap: nowrap; /* מונע ירידת שורה בנייד */
    }

    .number-ball { 
        width: 34px; 
        height: 34px; 
        background-color: #f8f9fa; 
        border-radius: 50%; 
        text-align: center; 
        line-height: 34px; 
        font-weight: bold; 
        border: 2px solid #4285F4; 
        color: #202124; 
        font-size: 14px;
        flex-shrink: 0;
    }
    
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05 !important; border-color: #EA4335 !important; }
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

def render_balls(nums, strong, actual_nums=[], actual_strong=-1):
    """פונקציה להצגת כדורים בשורה אחת צפופה"""
    html = '<div class="ball-container">'
    for n in nums:
        is_hit = "green-ball" if n in actual_nums else ""
        html += f'<div class="number-ball {is_hit}">{n}</div>'
    is_s_hit = "green-ball" if strong == actual_strong else ""
    html += f'<div class="number-ball strong-ball {is_s_hit}">{strong}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

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

def generate_gold_prediction(df):
    """חיזוי המשלב את חוקי הזהב"""
    try:
        # למידה מהיסטוריה (50 הגרלות אחרונות)
        all_nums_raw = df.head(50).iloc[:, 1:7].values.flatten()
        all_nums = [safe_int(n) for n in all_nums_raw if safe_int(n) > 0]
        
        if not all_nums: 
            return sorted(random.sample(range(1, 38), 6)), random.randint(1, 7)
            
        counts = pd.Series(all_nums).value_counts()
        hot = counts.head(12).index.tolist()
        cold = [n for n in range(1, 38) if n not in hot]
        
        # ניסיונות לייצר רצף שעומד בחוקי הזהב
        for _ in range(1000):
            # חוק 1: שילוב חמים וקרים
            pool = random.sample(hot, 4) + random.sample(cold, 2)
            nums = sorted(list(set(pool)))
            
            if len(nums) == 6:
                # חוק 2: סכום מספרים אידיאלי (90-155)
                if 90 <= sum(nums) <= 155:
                    # חוק 3: יחס זוגי/אי-זוגי (2:4 או 3:3 או 4:2)
                    evens = len([n for n in nums if n % 2 == 0])
                    if 2 <= evens <= 4:
                        return nums, random.randint(1, 7)
    except: pass
    return sorted(random.sample(range(1, 38), 6)), random.randint(1, 7)

# --- גוף האפליקציה ---
st.title("💰 Lotto AI Gold")
data = fetch_lotto_data()

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי", "📜 היסטוריה", "📊 דיוק"])
    next_id = safe_int(data.iloc[0, 0]) + 1

    with tab1:
        st.subheader(f"חיזוי להגרלה: {next_id}")
        if st.button("ייצר חיזוי זהב"):
            nums, strong = generate_gold_prediction(data)
            render_balls(nums, strong)
            st.session_state.my_predictions.append({
                'id': next_id, 'nums': nums, 'strong': strong, 'time': datetime.now().strftime("%H:%M")
            })
            st.success("החיזוי נשמר!")

    with tab2:
        if not st.session_state.my_predictions:
            st.info("אין חיזויים להצגה.")
        else:
            for pred in reversed(st.session_state.my_predictions):
                actual_row = data[data.iloc[:, 0].apply(safe_int) == pred['id']]
                a_nums = [safe_int(actual_row.iloc[0, i]) for i in range(1, 7)] if not actual_row.empty else []
                a_strong = safe_int(actual_row.iloc[0, 7]) if not actual_row.empty else -1
                
                st.write(f"🎯 הגרלה {pred['id']} ({pred['time']})")
                render_balls(pred['nums'], pred['strong'], a_nums, a_strong)
                st.write("---")

    with tab3:
        if len(data) > 0:
            st.write(f"סימולציה על הגרלה אחרונה ({data.iloc[0,0]}):")
            sim_nums, sim_strong = generate_gold_prediction(data.iloc[1:])
            real_nums = [safe_int(data.iloc[0, i]) for i in range(1, 7)]
            real_strong = safe_int(data.iloc[0, 7])
            render_balls(sim_nums, sim_strong, real_nums, real_strong)
            hits = len(set(sim_nums) & set(real_nums))
            st.info(f"פגיעות בסימולציה: {hits}")
else:
    st.error("שגיאה בטעינת נתונים.")