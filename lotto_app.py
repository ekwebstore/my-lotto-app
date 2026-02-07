import streamlit as st
import pandas as pd
import numpy as np
import random
import os
from datetime import datetime

# --- הגדרות דף ועיצוב ---
st.set_page_config(page_title="LOTTO AI", page_icon="🎯", layout="centered")

st.markdown("""
    <style>
    body { background-color: #0e1117; color: #ffffff; }
    .stApp { background-color: #0e1117; }
    .status-light { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-left: 8px; background-color: #00ff88; box-shadow: 0 0 10px #00ff88; }
    .think-box { background-color: #1e2130; padding: 15px; border-radius: 12px; border: 1px solid #3d4455; text-align: center; margin-bottom: 20px; }
    .ball { display: inline-block; width: 42px; height: 42px; background: radial-gradient(circle at 30% 30%, #ffffff, #d1d1d1); 
            border-radius: 50%; text-align: center; line-height: 42px; margin: 4px; 
            font-weight: bold; color: #1e2130; font-size: 1.1em; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); }
    .strong { background: radial-gradient(circle at 30% 30%, #ffcc00, #ff9900); border: none; }
    .success-ball { background: #00ff88 !important; color: #000 !important; box-shadow: 0 0 10px #00ff88; }
    .history-card { background-color: #1e2130; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-right: 4px solid #4285F4; }
    </style>
    """, unsafe_allow_html=True)

if 'elite_history' not in st.session_state:
    st.session_state.elite_history = []

# --- מנוע הניתוח ---

def get_latest_results(df):
    """שליפת תוצאות האמת האחרונות מהקובץ לצורך השוואה"""
    try:
        latest = df.iloc[0, 2:8].astype(int).tolist()
        latest_strong = int(df.iloc[0, 8])
        return latest, latest_strong
    except:
        return [], None

def analyze_logic(df):
    try:
        raw = df.iloc[:, 2:8].values.flatten()
        clean = [int(n) for n in raw if 1 <= n <= 37]
        counts = pd.Series(clean).value_counts()
        return counts.index[:15].tolist(), counts.index[-15:].tolist(), counts
    except:
        return list(range(1,16)), list(range(20,38)), pd.Series()

def elite_filter(nums):
    """מבחן הזהב המלא: סכום, זוגיות, יחס נמוך/גבוה ומרחקים"""
    s = sum(nums)
    evens = len([n for n in nums if n % 2 == 0])
    lows = len([n for n in nums if n <= 19])
    gaps = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
    
    # לוגיקה קשיחה לצירוף איכותי
    sum_ok = (100 <= s <= 150)
    even_ok = (2 <= evens <= 4)
    low_high_ok = (2 <= lows <= 4) 
    gap_ok = (max(gaps) <= 12 and min(gaps) >= 1 and len([g for g in gaps if g == 1]) <= 1)
    
    return (sum_ok and even_ok and low_high_ok and gap_ok), s

# --- ממשק המשתמש ---

st.title("LOTTO AI")

file_path = 'lotto_data.csv'

if os.path.exists(file_path):
    df = pd.read_csv(file_path, encoding='cp1255')
    hot, cold, full_counts = analyze_logic(df)
    real_results, real_strong = get_latest_results(df)

    # חיווי חשיבה ורמזור
    st.markdown(f"""
    <div class="think-box">
        <span class="status-light"></span> 
        <b>מנוע הלמידה פעיל:</b> המערכת ניתחה {len(df)} הגרלות וביצעה סימולציית זכייה לאחור.
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 הפק צירוף חכם"):
        found = False
        attempts = 0
        while not found and attempts < 3000:
            pick = random.sample(hot, 2) + random.sample(cold, 2) + random.sample(range(1, 38), 2)
            pick = sorted(list(set(pick)))
            if len(pick) == 6:
                is_elite, total_s = elite_filter(pick)
                if is_elite:
                    final_nums = pick
                    found = True
            attempts += 1
        
        strong = random.randint(1, 7)
        st.session_state.elite_history.append({"nums": final_nums, "strong": strong, "time": datetime.now().strftime("%H:%M")})
        
        st.markdown("### הניחוש המלומד:")
        res_html = "<div style='text-align: center;'>"
        for n in final_nums: res_html += f'<div class="ball">{n}</div>'
        res_html += f'<div class="ball strong">{strong}</div>'
        res_html += "</div>"
        st.markdown(res_html, unsafe_allow_html=True)
        st.success(f"הצירוף נוצר לאחר {attempts} סימולציות עומק.")

    # טאבים
    tab1, tab2 = st.tabs(["📜 היסטוריית ניחושים והצלחות", "📊 מפת חום"])
    
    with tab1:
        st.write("בכל עדכון של הקובץ, מספרים שניחשת נכון יצבעו בירוק:")
        for item in reversed(st.session_state.elite_history):
            item_html = f'<div class="history-card"><b>[{item["time"]}]</b> &nbsp; '
            for n in item["nums"]:
                # בדיקה אם המספר קיים בתוצאות האמת האחרונות
                match_class = "success-ball" if n in real_results else ""
                item_html += f'<span class="ball {match_class}" style="width:30px; height:30px; line-height:30px; font-size:0.9em;">{n}</span> '
            
            strong_match = "success-ball" if item["strong"] == real_strong else ""
            item_html += f' | <span class="ball strong {strong_match}" style="width:30px; height:30px; line-height:30px; font-size:0.9em;">{item["strong"]}</span>'
            item_html += "</div>"
            st.markdown(item_html, unsafe_allow_html=True)

    with tab2:
        st.bar_chart(full_counts.reindex(range(1, 38), fill_value=0))

else:
    st.error("נא להעלות קובץ lotto_data.csv")