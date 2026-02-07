import streamlit as st
import pandas as pd
import numpy as np
import random
import os
from datetime import datetime

# --- הגדרות דף ---
st.set_page_config(page_title="Lotto AI - Ultimate Logic", page_icon="🚥", layout="centered")

st.markdown("""
    <style>
    .status-light { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-left: 8px; }
    .light-green { background-color: #00C851; box-shadow: 0 0 8px #00C851; }
    .status-card { background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #dee2e6; font-size: 0.85em; text-align: center; }
    .ball { display: inline-block; width: 42px; height: 42px; background-color: white; 
            border-radius: 50%; text-align: center; line-height: 40px; margin: 4px; 
            font-weight: bold; border: 2px solid #4285F4; color: #4285F4; font-size: 1.1em; }
    .strong { border-color: #FBBC05; background-color: #FBBC05; color: white; }
    .history-item { background-color: #ffffff; padding: 10px; border-radius: 8px; 
                    margin-bottom: 8px; border-right: 5px solid #4285F4; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

if 'history_list' not in st.session_state:
    st.session_state.history_list = []

# --- מנוע ה-AI והקיצוניות המורחב ---

def analyze_and_extract_logic(df):
    try:
        raw_data = df.iloc[:, 2:8].values.flatten()
        clean_nums = [int(n) for n in raw_data if 1 <= n <= 37]
        counts = pd.Series(clean_nums).value_counts()
        hot = counts.index[:14].tolist()   
        cold = counts.index[-14:].tolist() 
        return hot, cold, counts
    except:
        return list(range(1, 15)), list(range(20, 38)), pd.Series()

def ultimate_extremity_test(nums):
    """מבחן קיצוניות מורחב: סכום, זוגיות, ומרחקים (Gaps)"""
    # 1. מבחן סכום (Sum Range)
    s = sum(nums)
    sum_pass = (90 <= s <= 160)
    
    # 2. מבחן זוגיות (Odd/Even)
    evens = len([n for n in nums if n % 2 == 0])
    even_pass = (2 <= evens <= 4)
    
    # 3. מבחן מרחקים (Gaps) ורצפים
    gaps = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
    consecutive = len([g for g in gaps if g == 1])
    # פוסלים אם יש יותר מ-2 מספרים עוקבים ברצף או יותר מדי רצפים
    gap_pass = (consecutive <= 1) and (max(gaps) <= 15) # מונע חור של יותר מ-15 מספרים
    
    # 4. מבחן פיזור (Decades)
    decades = [n // 10 for n in nums]
    # פוסלים אם יותר מ-3 מספרים נדחסו לאותו עשור
    decade_pass = all(decades.count(d) <= 3 for d in set(decades))
    
    return (sum_pass and even_pass and gap_pass and decade_pass), s, evens

# --- ממשק המשתמש ---

st.title("🚥 Lotto AI - Ultimate Control")
st.write("מנוע החיזוי משלב למידה היסטורית עם 4 מבחני קיצוניות (סכום, זוגיות, מרחקים ופיזור).")

file_path = 'lotto_data.csv'

if os.path.exists(file_path):
    df = pd.read_csv(file_path, encoding='cp1255')
    hot_list, cold_list, full_counts = analyze_and_extract_logic(df)

    # רמזורים מעודכנים
    st.markdown("### סטטוס מנוע AI")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="status-card"><span class="status-light light-green"></span>למידה</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="status-card"><span class="status-light light-green"></span>מרחקים</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="status-card"><span class="status-light light-green"></span>פיזור</div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="status-card"><span class="status-light light-green"></span>זוגיות</div>', unsafe_allow_html=True)

    if st.button("🚀 הפק צירוף אופטימלי"):
        found = False
        attempts = 0
        while not found and attempts < 2000:
            # הטמעת למידה: שילוב חם/קר
            pick = random.sample(hot_list, 2) + random.sample(cold_list, 2) + random.sample(range(1, 38), 2)
            pick = sorted(list(set(pick)))
            
            if len(pick) == 6:
                safe, s_val, e_val = ultimate_extremity_test(pick)
                if safe:
                    final_nums = pick
                    found = True
            attempts += 1
        
        strong = random.randint(1, 7)
        st.session_state.history_list.append({"time": datetime.now().strftime("%H:%M:%S"), "nums": final_nums, "strong": strong})
        
        # תצוגה
        st.markdown("### הניחוש המלומד והמסונן:")
        res_html = "<div style='text-align: center;'>"
        for n in final_nums: res_html += f'<div class="ball">{n}</div>'
        res_html += f'<div class="ball strong">{strong}</div>'
        res_html += "</div>"
        st.markdown(res_html, unsafe_allow_html=True)
        st.success(f"הצירוף עבר את כל 4 מבחני הקיצוניות לאחר {attempts} ניסיונות סינון.")

    # טאבים
    tab1, tab2 = st.tabs(["📜 היסטוריית הגרלות", "📊 מפת חום (למידה)"])
    with tab1:
        for item in reversed(st.session_state.history_list):
            st.markdown(f'<div class="history-item"><b>[{item["time"]}]</b> {", ".join(map(str, item["nums"]))} | חזק: {item["strong"]}</div>', unsafe_allow_html=True)
    with tab2:
        st.write("שכיחות המספרים עליה מתבססת הלמידה (1-37):")
        st.bar_chart(full_counts.reindex(range(1, 38), fill_value=0))

else:
    st.error("קובץ lotto_data.csv לא נמצא בתיקייה.")