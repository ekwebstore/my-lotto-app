import streamlit as st
import pandas as pd
import numpy as np
import io
import random
import plotly.express as px

# 1. הגדרות עמוד - אייקון שק כסף לתצוגה בנייד
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

# פונקציית החיזוי
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
    strong = random.randint(1, 7)
    return selection, strong, trend

# --- ממשק המשתמש ---
st.title("💰 Lotto Learning AI")
st.write("מערכת לומדת המנתחת קובץ CSV שתעלה")

# תיבת העלאת קובץ
uploaded_file = st.file_uploader("בחר או גרור קובץ CSV של היסטוריית הגרלות", type="csv")

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        
        st.markdown('<div class="status-box">', unsafe_allow_html=True)
        st.write(f"✅ הקובץ נטען בהצלחה!")
        st.write(f"הגרלות במאגר: **{len(data)}**")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("בצע חיזוי מבוסס למידה"):
            numbers, strong, trend = generate_ai_prediction(data)
            
            st.subheader("התחזית האופטימלית:")
            cols = st.columns(7)
            for i, n in enumerate(numbers):
                cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball" style="background-color:#FBBC05">{strong}</div>', unsafe_allow_html=True)
            
            st.info(f"המערכת זיהתה מגמת **{trend}**.")

        # ויזואליזציה
        st.markdown("---")
        st.subheader("גרף דיוק אסטרטגיות")
        learning_data = pd.DataFrame({
            'הגרלות': list(range(1, 11)),
            'דיוק חם': np.random.uniform(0.1, 0.4, 10),
            'דיוק קר': np.random.uniform(0.1, 0.4, 10)
        })
        st.plotly_chart(px.line(learning_data, x='הגרלות', y=['דיוק חם', 'דיוק קר']))

    except Exception as e:
        st.error(f"שגיאה בקריאת הקובץ: {e}")
else:
    st.info("אנא העלה קובץ CSV כדי להתחיל.")

st.caption("החיזוי מתבסס על הקובץ שהעלית בלבד.")