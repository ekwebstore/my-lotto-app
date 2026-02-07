import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
from datetime import datetime

# 1. הגדרות עמוד ואייקון (💰)
st.set_page_config(page_title="Lotto AI Pro", page_icon="💰", layout="centered")

# עיצוב CSS (המקורי והעובד שלך)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; border: none; }
    .number-ball { display: inline-block; width: 35px; height: 35px; background-color: #f8f9fa; border-radius: 50%; text-align: center; line-height: 35px; margin: 3px; font-weight: bold; border: 2px solid #4285F4; color: #202124; font-size: 14px; }
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05; border-color: #EA4335; }
    .history-card { padding: 12px; border-radius: 12px; border: 1px solid #dadce0; margin-bottom: 8px; background-color: #ffffff; direction: rtl; text-align: right; }
    .accuracy-box { padding: 10px; background-color: #e8f0fe; border-radius: 10px; margin-bottom: 5px; border-right: 5px solid #4285F4; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# זיכרון פנימי לשמירת חיזויים
if 'my_predictions' not in st.session_state:
    st.session_state.my_predictions = []

def safe_int(val):
    try:
        if pd.isna(val): return 0
        clean_val = ''.join(filter(str.isdigit, str(val)))
        return int(clean_val) if clean_val else 0
    except: return 0

@st.cache_data(ttl=60)
def fetch_lotto_data():
    url = "https://raw.githubusercontent.com/ekwebstore/my-lotto-app/main/lotto_data.csv"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8-sig', errors='ignore')))
            return df.dropna(how='all')
        return pd.DataFrame()
    except: return pd.DataFrame()

def generate_prediction(df):
    """הטמעת חוקי הלוגיקה בתוך המבנה המקורי"""
    try:
        # ניתוח 50 הגרלות אחרונות
        recent_data = df.head(50)
        all_nums_raw = recent_data.iloc[:, 1:7].values.flatten()
        all_nums = [safe_int(n) for n in all_nums_raw if safe_int(n) > 0]
        
        if not all_nums: 
            return sorted(random.sample(range(1, 38), 6)), random.randint(1, 7)
            
        counts = pd.Series(all_nums).value_counts()
        hot = counts.head(15).index.tolist()  # 15 הנפוצים ביותר
        cold = [n for n in range(1, 38) if n not in hot]
        
        # לולאת חיפוש רצף אידיאלי (עד 1000 ניסיונות)
        for _ in range(1000):
            # חוק 1: שילוב חמים וקרים (לרוב 4 חמים ו-2 קרים)
            pool = random.sample(hot, 4) + random.sample(cold, 2)
            nums = sorted(list(set(pool)))
            
            if len(nums) == 6:
                # חוק 2: סכום המספרים (חוק ה-120 הממוצע)
                total_sum = sum(nums)
                if 90 <= total_sum <= 155:
                    # חוק 3: איזון זוגי/אי-זוגי
                    evens = len([n for n in nums if n % 2 == 0])
                    if 2 <= evens <= 4:
                        # חוק 4: בדיקת רצפים (שלא יהיו יותר מ-2 עוקבים)
                        diffs = np.diff(nums)
                        if list(diffs).count(1) < 2:
                            return nums, random.randint(1, 7)
                            
    except Exception as e:
        pass # במקרה של תקלה בלוגיקה, יחזיר חיזוי אקראי בטוח
    return sorted(random.sample(range(1, 38), 6)), random.randint(1, 7)

st.title("💰 Lotto AI Pro")
data = fetch_lotto_data()

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["🔮 חיזוי חדש", "📜 היסטוריית חיזויים שלי", "📊 דיוק למידה"])

    last_lottery_id = safe_int(data.iloc[0, 0])
    next_lottery_id = last_lottery_id + 1

    with tab1:
        st.subheader(f"חיזוי להגרלה מספר: {next_lottery_id}")
        if st.button("ייצר חיזוי זהב ושמור"):
            nums, strong = generate_prediction(data)
            
            st.session_state.my_predictions.append({
                'id': next_lottery_id,
                'nums': nums,
                'strong': strong,
                'time': datetime.now().strftime("%H:%M:%S")
            })
            
            st.write("תוצאה לחיזוי הנוכחי:")
            cols = st.columns(7)
            for i, n in enumerate(nums):
                cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball strong-ball">{strong}</div>', unsafe_allow_html=True)
            st.success(f"חיזוי חוקי הזהב נרשם להגרלה {next_lottery_id}")

    with tab2:
        st.subheader("החיזויים שבוצעו במערכת")
        if not st.session_state.my_predictions:
            st.info("עדיין לא בוצעו חיזויים.")
        else:
            for pred in reversed(st.session_state.my_predictions):
                actual_row = data[data.iloc[:, 0].apply(safe_int) == pred['id']]
                actual_nums = []
                actual_strong = -1
                
                if not actual_row.empty:
                    actual_nums = [safe_int(actual_row.iloc[0, i]) for i in range(1, 7)]
                    actual_strong = safe_int(actual_row.iloc[0, 7])

                st.markdown(f"**הגרלה מיועדת: {pred['id']}** (בוצע ב-{pred['time']})")
                cols = st.columns(7)
                for i, n in enumerate(pred['nums']):
                    is_hit = "green-ball" if n in actual_nums else ""
                    cols[i].markdown(f'<div class="number-ball {is_hit}">{n}</div>', unsafe_allow_html=True)
                
                is_s_hit = "green-ball" if pred['strong'] == actual_strong else ""
                cols[6].markdown(f'<div class="number-ball strong-ball {is_s_hit}">{pred["strong"]}</div>', unsafe_allow_html=True)
                st.markdown("---")

    with tab3:
        st.subheader("רישום כמות פגיעות")
        if not st.session_state.my_predictions:
            st.write("אין נתונים.")
        else:
            for pred in st.session_state.my_predictions:
                actual_row = data[data.iloc[:, 0].apply(safe_int) == pred['id']]
                if not actual_row.empty:
                    actual_nums = [safe_int(actual_row.iloc[0, i]) for i in range(1, 7)]
                    actual_strong = safe_int(actual_row.iloc[0, 7])
                    hits = len(set(pred['nums']) & set(actual_nums))
                    strong_hit = " + חזק!" if pred['strong'] == actual_strong else ""
                    st.markdown(f'<div class="accuracy-box">הגרלה <b>{pred["id"]}</b>: נמצאו <b>{hits}</b> פגיעות נכונות{strong_hit}</div>', unsafe_allow_html=True)
                else:
                    st.write(f"הגרלה {pred['id']}: ממתין לתוצאות אמת.")

else:
    st.error("לא ניתן לטעון את קובץ הנתונים.")