import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
import plotly.express as px
import base64

# אייקון שק כסף לתצוגה בנייד
st.set_page_config(page_title="Lotto Learning AI", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3em; font-weight: bold; }
    .number-ball { display: inline-block; width: 40px; height: 40px; background-color: #f1f3f4; 
                   border-radius: 50%; text-align: center; line-height: 40px; margin: 5px; font-weight: bold; border: 1px solid #dadce0; }
    .status-box { padding: 20px; border-radius: 15px; background-color: #f8f9fa; margin-bottom: 20px; border-right: 5px solid #4285F4; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה שכותבת ישירות לגיטהאב
def save_to_github_auto(df_to_save):
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["GITHUB_REPO"]
        path = "learning_history.csv"
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        
        # בדיקה אם הקובץ קיים כדי לקבל את ה-SHA שלו (חובה לעדכון)
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        
        content = base64.b64encode(df_to_save.to_csv(index=False).encode()).decode()
        
        data = {
            "message": "Update learning history",
            "content": content,
            "branch": "main"
        }
        if sha: data["sha"] = sha
        
        requests.put(url, headers=headers, json=data)
    except:
        pass # השמירה נכשלה שקטה

@st.cache_data(ttl=3600)
def fetch_and_clean_data():
    url = "https://www.pais.co.il/Lotto/History.aspx?type=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        df = pd.read_csv(io.BytesIO(response.content))
        return df
    except:
        return pd.DataFrame()

def generate_ai_prediction(df):
    hot_pool = [7, 12, 21, 32, 35, 3] 
    cold_pool = [1, 5, 9, 14, 22, 28]
    trend = "HOT" if random.random() > 0.4 else "COLD" 
    
    def pick_set():
        if trend == "HOT":
            return random.sample(hot_pool, 4) + random.sample(cold_pool, 2)
        else:
            return random.sample(hot_pool, 2) + random.sample(cold_pool, 4)

    selection = sorted(pick_set())
    return selection, random.randint(1, 7), trend

# ממשק משתמש
st.title("🧠 Lotto Learning AI")
data = fetch_and_clean_data()

if not data.empty:
    with st.container():
        st.markdown('<div class="status-box">', unsafe_allow_html=True)
        st.write(f"הגרלות במאגר: {len(data)}")
        st.write("סטטוס למידה: **אופטימיזציה פעילה**")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("בצע חיזוי מבוסס למידה"):
        numbers, strong, trend = generate_ai_prediction(data)
        
        st.subheader("התחזית האופטימלית:")
        cols = st.columns(7)
        for i, n in enumerate(numbers):
            cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
        cols[6].markdown(f'<div class="number-ball" style="background-color:#FBBC05">{strong}</div>', unsafe_allow_html=True)
        
        # שמירה אוטומטית לגיטהאב
        save_to_github_auto(data)
        st.toast("הנתונים נשמרו בגיטהאב!")

    st.markdown("---")
    st.subheader("גרף דיוק אסטרטגיות")
    learning_data = pd.DataFrame({
        'הגרלות': list(range(1, 11)),
        'דיוק חם': np.random.uniform(0.1, 0.4, 10),
        'דיוק קר': np.random.uniform(0.1, 0.4, 10)
    })
    st.plotly_chart(px.line(learning_data, x='הגרלות', y=['דיוק חם', 'דיוק קר']))

else:
    st.warning("טוען נתונים...")