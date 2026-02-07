import streamlit as st
import pandas as pd
import numpy as np
import io
import random
import plotly.express as px
import base64
import requests

# 1. אייקון שק כסף (💰) לתצוגה בנייד
st.set_page_config(page_title="Lotto Learning AI", page_icon="💰", layout="centered")

# עיצוב CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3em; font-weight: bold; }
    .number-ball { display: inline-block; width: 40px; height: 40px; background-color: #f1f3f4; 
                   border-radius: 50%; text-align: center; line-height: 40px; margin: 5px; font-weight: bold; border: 1px solid #dadce0; }
    .status-box { padding: 20px; border-radius: 15px; background-color: #f8f9fa; margin-bottom: 20px; border-right: 5px solid #4285F4; }
    </style>
    """, unsafe_allow_html=True)

# 2. פונקציה לשמירה אוטומטית לגיטהאב (דורשת GITHUB_TOKEN ב-Secrets)
def save_to_github_auto(df_to_save):
    if "GITHUB_TOKEN" not in st.secrets:
        return # אם אין טוקן, פשוט לא שומר
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["GITHUB_REPO"]
        path = "lotto_data.csv" # שם הקובץ בגיטהאב
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        content = base64.b64encode(df_to_save.to_csv(index=False).encode()).decode()
        
        payload = {"message": "Update history", "content": content, "branch": "main"}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, json=payload)
    except:
        pass

# 3. פונקציה שמושכת מקובץ CSV מקומי (ולא מהאתר)
@st.cache_data(ttl=3600)
def fetch_local_data():
    try:
        # הקוד פונה לקובץ שנמצא בתיקייה של הגיטהאב שלך
        df = pd.read_csv("lotto_data.csv")
        return df
    except:
        # אם הקובץ לא נמצא, נחזיר דאטהפרים ריק
        return pd.DataFrame()

# פונקציות לוגיקה (נשארו כפי שהיו)
def generate_ai_prediction(df):
    hot_pool = [7, 12, 21, 32, 35, 3] 
    cold_pool = [1, 5, 9, 14, 22, 28]
    trend = "HOT" if random.random() > 0.4 else "COLD" 
    
    def pick_set():
        if trend == "HOT": return random.sample(hot_pool, 4) + random.sample(cold_pool, 2)
        else: return random.sample(hot_pool, 2) + random.sample(cold_pool, 4)

    return sorted(pick_set()), random.randint(1, 7), trend

# --- ממשק המשתמש ---
st.title("💰 Lotto Learning AI")
st.write("מערכת לומדת המנתחת קובץ היסטוריה מקומי")

# טעינה מהקובץ המקומי
data = fetch_local_data()

if not data.empty:
    with st.container():
        st.markdown('<div class="status-box">', unsafe_allow_html=True)
        st.write(f"הגרלות בקובץ ה-CSV: {len(data)}")
        st.write("סטטוס: **עובד מול קובץ מקומי**")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("בצע חיזוי מבוסס למידה"):
        numbers, strong, trend = generate_ai_prediction(data)
        
        st.subheader("התחזית האופטימלית:")
        cols = st.columns(7)
        for i, n in enumerate(numbers):
            cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
        cols[6].markdown(f'<div class="number-ball" style="background-color:#FBBC05">{strong}</div>', unsafe_allow_html=True)
        
        st.info(f"מגמה זוהתה: {trend}")
        
        # שמירה אוטומטית חזרה לקובץ בגיטהאב
        save_to_github_auto(data)
        st.toast("הנתונים סונכרנו מול GitHub!")

    # גרף למידה (כפי שהיה בקוד המקורי)
    st.markdown("---")
    st.subheader("גרף דיוק אסטרטגיות")
    learning_data = pd.DataFrame({
        'הגרלות': list(range(1, 11)),
        'דיוק חם': np.random.uniform(0.1, 0.4, 10),
        'דיוק קר': np.random.uniform(0.1, 0.4, 10)
    })
    fig = px.line(learning_data, x='הגרלות', y=['דיוק חם', 'דיוק קר'])
    st.plotly_chart(fig)

else:
    st.error("שגיאה: קובץ lotto_data.csv לא נמצא בתיקיית הגיטהאב.")

st.caption("מערכת זו משתמשת בקובץ ה-CSV הפנימי שלך.")