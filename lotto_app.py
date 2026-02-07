import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
import plotly.express as px
from datetime import datetime

# 1. הגדרות עמוד ואייקון (יופיע בנייד)
st.set_page_config(page_title="Lotto AI Pro", page_icon="💰", layout="centered")

# עיצוב CSS מתקדם למראה אפליקציה
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5em; background-color: #4285F4; color: white; font-weight: bold; border: none; }
    .number-ball { display: inline-block; width: 38px; height: 38px; background-color: #f8f9fa; border-radius: 50%; text-align: center; line-height: 38px; margin: 4px; font-weight: bold; border: 2px solid #4285F4; color: #202124; }
    .strong-ball { background-color: #FBBC05; border-color: #EA4335; }
    .card { padding: 20px; border-radius: 15px; background-color: #f1f3f4; margin-bottom: 20px; border-right: 6px solid #34A853; }
    .history-card { padding: 10px; border-radius: 10px; border: 1px solid #dadce0; margin-top: 10px; background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data():
    url = "https://www.pais.co.il/Lotto/History.aspx?type=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        # קריאת הקובץ - מפעל הפיס משתמשים בקידוד עברי
        df = pd.read_csv(io.BytesIO(response.content))
        # ניקוי עמודות - בחירת העמודות הרלוונטיות בלבד
        # בדרך כלל: תאריך (1), מספרים (2-7), חזק (8)
        clean_df = df.iloc[:, [1, 2, 3, 4, 5, 6, 7, 8]].copy()
        clean_df.columns = ['date', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'strong']
        return clean_df
    except:
        return pd.DataFrame()

# פונקציה לחישוב חיזוי (מבוססת למידה סטטיסטית)
def get_ai_prediction(df):
    all_nums = df[['n1', 'n2', 'n3', 'n4', 'n5', 'n6']].values.flatten()
    counts = pd.Series(all_nums).value_counts()
    hot = counts.head(12).index.tolist()
    cold = [n for n in range(1, 38) if n not in hot]
    
    # אסטרטגיה: 3 חמים, 2 קרים, 1 אקראי + סינון סכום
    for _ in range(50):
        pick = random.sample(hot, 3) + random.sample(cold, 2) + random.sample(range(1, 38), 1)
        pick = sorted(list(set(pick)))
        if len(pick) == 6 and 90 <= sum(pick) <= 155:
            return pick, random.randint(1, 7)
    return sorted(random.sample(range(1, 38), 6)), random.randint(1, 7)

# --- תצוגת האפליקציה ---

st.title("💰 Lotto AI Predictor")
data = load_data()

if not data.empty:
    # כרטיסיית בקרה: בדיקת ביצועי המודל על ההגרלה האחרונה
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔍 בקרת דיוק (Backtesting)")
    
    # נבצע חיזוי וירטואלי ונשווה להגרלה האחרונה
    actual_last = set(data.iloc[0][['n1', 'n2', 'n3', 'n4', 'n5', 'n6']].values)
    actual_strong = data.iloc[0]['strong']
    
    # סימולציה של מה המודל היה מוציא
    sim_nums, sim_strong = get_ai_prediction(data.iloc[1:])
    hits = len(set(sim_nums).intersection(actual_last))
    strong_hit = "כן" if sim_strong == actual_strong else "לא"
    
    st.write(f"בהגרלה האחרונה ({data.iloc[0]['date']}):")
    st.write(f"🎯 המודל פגע ב-**{hits}** מספרים.")
    st.write(f"🌟 פגיעה במספר חזק: **{strong_hit}**")
    st.markdown('</div>', unsafe_allow_html=True)

    # כרטיסיית חיזוי
    if st.button("ייצר חיזוי להגרלה הבאה"):
        nums, strong = get_ai_prediction(data)
        st.subheader("🔮 התחזית להיום:")
        cols = st.columns(7)
        for i, v in enumerate(nums):
            cols[i].markdown(f'<div class="number-ball">{v}</div>', unsafe_allow_html=True)
        cols[6].markdown(f'<div class="number-ball strong-ball">{strong}</div>', unsafe_allow_html=True)
        st.balloons()

    # כרטיסיית היסטוריה
    st.markdown("---")
    st.subheader("📜 היסטוריית הגרלות אחרונות")
    for i in range(5):
        row = data.iloc[i]
        st.markdown(f"""
        <div class="history-card">
            <strong>תאריך: {row['date']}</strong><br>
            {row['n1']}, {row['n2']}, {row['n3']}, {row['n4']}, {row['n5']}, {row['n6']} | חזק: {row['strong']}
        </div>
        """, unsafe_allow_html=True)

    # מפת חום
    st.markdown("---")
    st.subheader("📊 מפת חום (שכיחות)")
    all_draws = data[['n1', 'n2', 'n3', 'n4', 'n5', 'n6']].values.flatten()
    fig = px.histogram(x=all_draws, nbins=37, labels={'x':'מספר', 'y':'שכיחות'}, color_discrete_sequence=['#34A853'])
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("לא ניתן לטעון נתונים. בדוק חיבור אינטרנט.")

st.caption(f"עודכן לאחרונה: {datetime.now().strftime('%d/%m/%Y %H:%M')}")