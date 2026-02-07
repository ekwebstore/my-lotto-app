import streamlit as st
import pandas as pd
import numpy as np
import io
import random
import plotly.express as px

# 1. הגדרות עמוד - אייקון שק כסף לתצוגה בנייד
st.set_page_config(page_title="Lotto Learning AI", page_icon="💰", layout="centered")

# עיצוב CSS בסגנון נקי
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3em; font-weight: bold; }
    .number-ball { display: inline-block; width: 40px; height: 40px; background-color: #f1f3f4; 
                   border-radius: 50%; text-align: center; line-height: 40px; margin: 5px; font-weight: bold; border: 1px solid #dadce0; }
    .status-box { padding: 20px; border-radius: 15px; background-color: #f8f9fa; margin-bottom: 20px; border-right: 5px solid #4285F4; }
    .upload-text { font-weight: bold; color: #4285F4; }
    </style>
    """, unsafe_allow_html=True)

# 2. כותרת וממשק העלאה
st.title("💰 Lotto Learning AI")
st.write("מערכת לומדת המנתחת קובץ CSV שתעלה")

# תיבת העלאת קובץ - פותר את שגיאת "קובץ לא נמצא"
uploaded_file = st.file_uploader("בחר או גרור קובץ CSV של היסטוריית הגרלות", type="csv")

def generate_ai_prediction(df):
    # הלוגיקה המקורית שלך
    hot_pool = [7, 12, 21, 32, 35, 3] 
    cold_pool = [1, 5, 9, 14, 22, 28]
    trend = "HOT" if random.random() > 0.4 else "COLD" 
    
    def pick_set():
        if trend == "HOT":
            return random.sample(hot_pool, 4) + random.sample(cold_pool, 2)
        else:
            return random.sample(hot_pool, 2) + random.sample(cold_pool, 4)

    selection = sorted(pick_set())
    strong = random.randint(1, 7)
    return selection, strong, trend

# בדיקה אם הועלה קובץ
if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        
        with st.container():
            st.markdown('<div class="status-box">', unsafe_allow_html=True)
            st.write(f"✅ הקובץ נטען בהצלחה!")
            st.write(f"הגרלות במאגר: **{len(data)}**")
            st.write("סטטוס: **מנתח נתונים בזמן אמת**")
            st.markdown('</div>', unsafe_allow_html=True)

        if st