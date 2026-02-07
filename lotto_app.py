import streamlit as st
import pandas as pd
import numpy as np
import random
import os
from datetime import datetime

# --- הגדרות דף ---
st.set_page_config(page_title="Lotto AI Master", page_icon="🎯", layout="centered")

# עיצוב CSS נקי ומותאם לנייד
st.markdown("""
    <style>
    .ball { display: inline-block; width: 42px; height: 42px; background-color: white; 
            border-radius: 50%; text-align: center; line-height: 42px; margin: 4px; 
            font-weight: bold; border: 2px solid #4285F4; font-size: 1.1em; color: #202124; }
    .strong { border-color: #FBBC05; background-color: #FBBC05; color: white; }
    .history-item { background-color: #f1f3f4; padding: 10px; border-radius: 8px; 
                    margin-bottom: 5px; font-family: sans-serif; border-right: 4px solid #4285F4; }
    .hot-tag { color: #d93025; font-weight: bold; }
    .cold-tag { color: #1967d2; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול זיכרון היסטוריה ---
if 'lotto_history' not in st.session_state:
    st.session_state.lotto_history = []

# --- פונקציות ניתוח ---

def analyze_lotto_data(df):
    """מנתח את הקובץ ומוציא מספרים חמים וקרים באמת"""
    try:
        # חילוץ המספרים (עמודות 2 עד 7 ב-CSV של הפיס)
        raw_numbers = df.iloc[:, 2:8].values.flatten()
        clean_nums = [int(n) for n in raw_numbers if 1 <= n <= 37]
        counts = pd.Series(clean_nums).value_counts()
        
        hot = counts.index[:12].tolist()  # 12 הכי נפוצים
        cold = counts.index[-12:].tolist() # 12 הכי נדירים
        return hot, cold, counts
    except:
        return list(range(1, 13)), list(range(26, 38)), pd.Series()

def run_safety_check(nums):
    """מבחן קיצוניות: סכום וזוגיות"""
    s = sum(nums)
    evens = len([n for n in nums if n % 2 == 0])
    # תנאים לצירוף מאוזן
    return (90 <= s <= 155) and (2 <= evens <= 4), s

# --- ממשק המשתמש ---

st.title("🎯 לוטו AI - חכם ומדויק")

file_path = 'lotto_data.csv'

if os.path.exists(file_path):
    df = pd.read_csv(file_path, encoding='cp1255')
    hot_list, cold_list, full_counts = analyze_lotto_data(df)
    
    # תצוגת למידה מהירה
    st.markdown("### 🔍 דוח למידה מהקובץ")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"🔥 <span class='hot-tag'>מספרים חמים:</span> {', '.join(map(str, hot_list[:6]))}", unsafe_allow_html=True)
    with c2:
        st.markdown(f"❄️ <span class='cold-tag'>מספרים קרים:</span> {', '.join(map(str, cold_list[:6]))}", unsafe_allow_html=True)

    st.divider()

    if st.button("🚀 ייצר צירוף חכם והוסף להיסטוריה"):
        found = False
        attempts = 0
        while not found and attempts < 1000:
            # אסטרטגיה: שילוב של חמים, קרים ואקראיים בטווח 1-37
            pick = random.sample(hot_list, 2) + random.sample(cold_list, 2) + random.sample(range(1, 38), 2)
            pick = sorted(list(set(pick)))
            if len(pick) == 6:
                safe, total_sum = run_safety_check(pick)
                if safe:
                    found = True
                    final_nums = pick
            attempts += 1
        
        strong_num = random.randint(1, 7)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # שמירה להיסטוריה
        st.session_state.lotto_history.append({
            "time": timestamp,
            "nums": final_nums,
            "strong": strong_num
        })
        
        # תצוגת התוצאה הנוכחית
        st.markdown("### הניחוש המומלץ:")
        res_html = "<div style='text-align: center;'>"
        for n in final_nums:
            res_html += f'<div class="ball">{n}</div>'
        res_html += f'<div class="ball strong">{strong_num}</div>'
        res_html += "</div>"
        st.markdown(res_html, unsafe_allow_html=True)
        st.caption(f"הצירוף עבר מבחן קיצוניות (סכום: {total_sum})")

    # --- טאבים למידע נוסף ---
    tab1, tab2 = st.tabs(["📜 היסטוריית תחזיות", "📊 מפת חום מלאה"])
    
    with tab1:
        if st.session_state.lotto_history:
            for item in reversed(st.session_state.lotto_history):
                nums_str = ", ".join(map(str, item['nums']))
                st.markdown(f"""
                <div class="history-item">
                    <b>{item['time']}</b> | {nums_str} | <span style="color:#f2ab26">חזק: {item['strong']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("עדיין לא נוצרו תחזיות.")

    with tab2:
        st.write("שכיחות הופעת מספרים (1-37):")
        if not full_counts.empty:
            # סידור הגרף לפי סדר המספרים 1-37
            freq_data = full_counts.reindex(range(1, 38), fill_value=0)
            st.bar_chart(freq_data)
        else:
            st.write("אין מספיק נתונים להצגת גרף.")

else:
    st.error("לא נמצא קובץ נתונים!")
    st.info("אנא העלה קובץ בשם lotto_data.csv לתיקיית ה-GitHub שלך.")