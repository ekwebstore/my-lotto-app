import streamlit as st
import pandas as pd
import numpy as np
import random
import os
from datetime import datetime

# --- הגדרות דף ועיצוב RTL ---
st.set_page_config(page_title="LOTTO AI", page_icon="🎯", layout="centered")

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    div.stButton > button { width: 100%; border-radius: 20px; background-color: #4285F4; color: white; font-weight: bold; }
    .think-box { background-color: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #dee2e6; text-align: right; margin-bottom: 20px; border-right: 5px solid #00C851; }
    .status-light { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-left: 10px; background-color: #00C851; box-shadow: 0 0 8px #00C851; }
    .ball { display: inline-block; width: 38px; height: 38px; background-color: #ffffff; border-radius: 50%; text-align: center; line-height: 36px; margin: 3px; font-weight: bold; color: #202124; font-size: 1em; border: 2px solid #4285F4; }
    .strong { background-color: #FBBC05; border-color: #f2ab26; color: white; }
    .success-ball { background-color: #00C851 !important; color: white !important; border-color: #007E33 !important; }
    .history-card { background-color: #ffffff; padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #eee; border-right: 5px solid #4285F4; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

if 'ai_history' not in st.session_state:
    st.session_state.ai_history = []

# --- פונקציות מנוע ---

def get_data_info(df):
    """שליפת מספר ההגרלה האחרונה ותוצאותיה"""
    try:
        # הנחת עבודה: עמודה 0 היא מספר הגרלה, 2-7 מספרים, 8 חזק
        last_draw_num = int(df.iloc[0, 0])
        return last_draw_num, df
    except:
        return 0, df

def check_hits(prediction_nums, prediction_strong, target_draw_num, df):
    """בדיקה האם החיזוי פגע בתוצאות של הגרלה ספציפית"""
    draw_row = df[df.iloc[:, 0] == target_draw_num]
    if not draw_row.empty:
        real_nums = draw_row.iloc[0, 2:8].astype(int).tolist()
        real_strong = int(draw_row.iloc[0, 8])
        hits = [n for n in prediction_nums if n in real_nums]
        strong_hit = (prediction_strong == real_strong)
        return hits, strong_hit, len(hits)
    return [], False, None

def analyze_and_filter(df):
    raw = df.iloc[:, 2:8].values.flatten()
    counts = pd.Series([int(n) for n in raw if 1 <= n <= 37]).value_counts()
    hot, cold = counts.index[:15].tolist(), counts.index[-15:].tolist()
    
    # חיפוש צירוף שעומד במבחן הזהב
    for _ in range(3000):
        pick = sorted(list(set(random.sample(hot, 2) + random.sample(cold, 2) + random.sample(range(1, 38), 2))))
        if len(pick) == 6:
            s = sum(pick)
            gaps = [pick[i+1] - pick[i] for i in range(len(pick)-1)]
            if (100 <= s <= 155) and (2 <= len([n for n in pick if n % 2 == 0]) <= 4) and (max(gaps) <= 12):
                return pick
    return sorted(random.sample(range(1, 38), 6))

# --- ממשק משתמש ---

st.markdown('<div class="main">', unsafe_allow_html=True)
st.title("LOTTO AI")

file_path = 'lotto_data.csv'

if os.path.exists(file_path):
    df = pd.read_csv(file_path, encoding='cp1255')
    last_id, data = get_data_info(df)

    st.markdown(f"""
    <div class="think-box">
        <span class="status-light"></span> 
        <b>מנוע AI פעיל:</b> הגרלה אחרונה במערכת: {last_id}. החיזויים יושוו אוטומטית כשהקובץ יתעדכן.
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 הפק חיזוי חכם להגרלה הבאה"):
        final_nums = analyze_and_filter(df)
        strong = random.randint(1, 7)
        
        st.session_state.ai_history.append({
            "target_draw": last_id + 1,
            "nums": final_nums,
            "strong": strong,
            "time": datetime.now().strftime("%H:%M")
        })
        
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        res_html = "".join([f'<div class="ball">{n}</div>' for n in final_nums])
        res_html += f'<div class="ball strong">{strong}</div>'
        st.markdown(res_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.success(f"הופק חיזוי להגרלה מספר {last_id + 1}")

    tab1, tab2 = st.tabs(["📜 היסטוריית חיזויים והשוואה", "📈 מדד דיוק חיזויים"])
    
    with tab1:
        for item in reversed(st.session_state.ai_history):
            hits, strong_hit, score = check_hits(item["nums"], item["strong"], item["target_draw"], df)
            
            status_txt = f"ממתין להגרלה {item['target_draw']}" if score is None else f"תוצאות הגרלה {item['target_draw']}"
            
            item_html = f'<div class="history-card"><b>{status_txt}</b> (בוצע ב-{item["time"]})<br>'
            for n in item["nums"]:
                c = "success-ball" if n in hits else ""
                item_html += f'<span class="ball {c}">{n}</span>'
            
            sc = "success-ball" if strong_hit else ""
            item_html += f' | <span class="ball strong {sc}">{item["strong"]}</span></div>'
            st.markdown(item_html, unsafe_allow_html=True)

    with tab2:
        st.write("כמות פגיעות בכל הגרלה (מתוך החיזויים שבוצעו):")
        success_data = []
        for item in st.session_state.ai_history:
            _, _, score = check_hits(item["nums"], item["strong"], item["target_draw"], df)
            if score is not None:
                success_data.append({"הגרלה": str(item["target_draw"]), "פגיעות": score})
        
        if success_data:
            chart_df = pd.DataFrame(success_data)
            st.bar_chart(chart_df.set_index("הגרלה"))
        else:
            st.info("כאן יופיע גרף ברגע שתעלה קובץ עם תוצאות להגרלות שחזית.")

else:
    st.error("קובץ lotto_data.csv חסר.")

st.markdown('</div>', unsafe_allow_html=True)