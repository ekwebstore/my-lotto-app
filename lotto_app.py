import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
from datetime import datetime

# 1. הגדרות עמוד ואייקון (💰)
st.set_page_config(page_title="Lotto AI Pro", page_icon="💰", layout="centered")

# עיצוב CSS - כדורים, כרטיסיות וצבעים
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; border: none; }
    .number-ball { display: inline-block; width: 38px; height: 38px; background-color: #f8f9fa; border-radius: 50%; text-align: center; line-height: 38px; margin: 4px; font-weight: bold; border: 2px solid #4285F4; color: #202124; }
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05; border-color: #EA4335; }
    .history-card { padding: 15px; border-radius: 12px; border: 1px solid #dadce0; margin-bottom: 10px; background-color: #ffffff; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציית משיכת נתונים מגיטהאב ציבורי ---
@st.cache_data(ttl=600)
def fetch_github_csv(file_name):
    # כאן עליך להחליף ליוזר ולשם ה-Repo שלך
    USER = "YOUR_USERNAME" 
    REPO = "YOUR_REPO_NAME"
    url = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{file_name}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return pd.read_csv(io.StringIO(response.content))
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- מנגנון החיזוי - חוקי הזהב (סכום, מרחק, זוגיות) ---
def generate_gold_prediction(df):
    all_draws = df.iloc[:, 1:7].values.flatten()
    counts = pd.Series(all_draws).value_counts()
    hot = counts.head(12).index.tolist()
    cold = [n for n in range(1, 38) if n not in hot]
    
    trend = "HOT" if random.random() > 0.4 else "COLD"
    
    for _ in range(200): # ניסיונות לייצור צירוף שעומד בחוקים
        pool = random.sample(hot, 4) + random.sample(cold, 2) if trend == "HOT" else random.sample(hot, 2) + random.sample(cold, 4)
        nums = sorted(list(set(pool)))
        if len(nums) < 6: continue
        
        # חוקי הזהב
        if not (90 <= sum(nums) <= 155): continue # חוק הסכום
        diffs = np.diff(nums)
        if any(diffs == 1) and list(diffs).count(1) > 1: continue # חוק המרחק
        evens = len([n for n in nums if n % 2 == 0])
        if evens < 2 or evens > 4: continue # חוק האיזון
        
        return nums, random.randint(1, 7), trend
    return sorted(random.sample(range(1, 38), 6)), 1, "RANDOM"

# --- ממשק המשתמש ---
st.title("💰 Lotto AI Predictor")

# טעינת נתונים (שימוש בשם הקובץ שביקשת)
data = fetch_github_csv("lotto_data.csv")

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי חדש", "📜 היסטוריית הגרלות", "✅ דיוק למידה"])

    with tab1:
        st.subheader("חיזוי מבוסס חוקי הזהב")
        if st.button("ייצר חיזוי להגרלה הבאה"):
            nums, strong, trend = generate_gold_prediction(data)
            
            st.write(f"מגמה זוהתה: **{trend}**")
            cols = st.columns(7)
            for i, n in enumerate(nums):
                cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball strong-ball">{strong}</div>', unsafe_allow_html=True)
            st.balloons()
            
            # הערה: ללא Token, החיזוי יוצג אך לא יישמר בגיטהאב אוטומטית

    with tab2:
        st.subheader("הגרלות אחרונות מהקובץ")
        for i in range(min(10, len(data))):
            row = data.iloc[i]
            # הנחת מבנה: עמודה 0=תאריך/ID, 1-6=מספרים, 7=חזק
            st.markdown(f"""
            <div class="history-card">
                <strong>הגרלה: {row[0]}</strong><br>
                {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}, {row[6]} | <b>חזק: {row[7]}</b>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader("בדיקת דיוק רטרואקטיבית")
        st.write("בדיקה: לו היינו מנבאים את ההגרלה האחרונה (Backtest):")
        
        # לוקחים את כל הנתונים חוץ מההגרלה הכי חדשה ומנבאים אותה
        test_data = data.iloc[1:]
        actual_row = data.iloc[0]
        actual_nums = [int(actual_row[i]) for i in range(1, 7)]
        actual_strong = int(actual_row[7])
        
        sim_nums, sim_strong, _ = generate_gold_prediction(test_data)
        
        cols = st.columns(7)
        for i, sn in enumerate(sim_nums):
            is_hit = "green-ball" if sn in actual_nums else ""
            cols[i].markdown(f'<div class="number-ball {is_hit}">{sn}</div>', unsafe_allow_html=True)
        
        is_s_hit = "green-ball" if sim_strong == actual_strong else ""
        cols[6].markdown(f'<div class="number-ball strong-ball {is_s_hit}">{sim_strong}</div>', unsafe_allow_html=True)
        
        st.caption("מספרים בירוק = פגיעה בחיזוי הסימולציה")

else:
    st.error("שגיאה: לא הצלחתי למשוך את הקובץ lotto_data.csv מגיטהאב. וודא שה-URL תקין והמאגר ציבורי.")

st.caption(f"עודכן לאחרונה: {datetime.now().strftime('%d/%m/%Y %H:%M')}")