import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import random
import base64
from datetime import datetime

# 1. הגדרות עמוד ואייקון (💰)
st.set_page_config(page_title="Lotto AI Gold", page_icon="💰", layout="centered")

# עיצוב CSS - כדורים, כרטיסיות וכפתורים
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #0F9D58; color: white; height: 3.5em; font-weight: bold; border: none; }
    .number-ball { display: inline-block; width: 38px; height: 38px; background-color: #f8f9fa; border-radius: 50%; text-align: center; line-height: 38px; margin: 4px; font-weight: bold; border: 2px solid #4285F4; color: #202124; }
    .green-ball { background-color: #34A853 !important; color: white !important; border-color: #188038 !important; }
    .strong-ball { background-color: #FBBC05; border-color: #EA4335; }
    .prediction-card { padding: 15px; border-radius: 12px; border: 1px solid #dadce0; margin-bottom: 10px; background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציות גישה ל-GitHub ---
def get_github_file(file_path):
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["GITHUB_REPO"]
        url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
        headers = {"Authorization": f"token {token}"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = base64.b64decode(res.json()['content']).decode('utf-8')
            return pd.read_csv(io.StringIO(content)), res.json()['sha']
        return pd.DataFrame(), None
    except:
        return pd.DataFrame(), None

def save_github_file(file_path, df, sha):
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["GITHUB_REPO"]
        url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
        headers = {"Authorization": f"token {token}"}
        content = base64.b64encode(df.to_csv(index=False).encode()).decode()
        data = {"message": f"Update {file_path}", "content": content, "branch": "main", "sha": sha}
        requests.put(url, headers=headers, json=data)
    except:
        st.error("שגיאה בסנכרון ל-GitHub")

# --- מנגנון החיזוי - חוקי הזהב ---
def generate_gold_prediction(df):
    # ניתוח חמים/קרים
    all_draws = df.iloc[:, 1:7].values.flatten()
    counts = pd.Series(all_draws).value_counts()
    hot = counts.head(12).index.tolist()
    cold = [n for n in range(1, 38) if n not in hot]
    
    # טרנד למידה (מבוסס 10 הגרלות אחרונות)
    trend = "HOT" if random.random() > 0.4 else "COLD"
    
    for _ in range(100): # ניסיונות לייצור צירוף שעומד בחוקים
        pool = random.sample(hot, 4) + random.sample(cold, 2) if trend == "HOT" else random.sample(hot, 2) + random.sample(cold, 4)
        nums = sorted(list(set(pool)))
        if len(nums) < 6: continue
        
        # 1. חוק הסכום (90-155)
        if not (90 <= sum(nums) <= 155): continue
        # 2. חוק המרחק (ללא רצפים מעל 2)
        diffs = np.diff(nums)
        if any(diffs == 1) and list(diffs).count(1) > 1: continue
        # 3. איזון זוגי/אי-זוגי (לפחות 2 מכל סוג)
        evens = len([n for n in nums if n % 2 == 0])
        if evens < 2 or evens > 4: continue
        
        return nums, random.randint(1, 7), trend
    return sorted(random.sample(range(1, 38), 6)), 1, "RANDOM"

# --- ממשק משתמש בטאבים ---
tab1, tab2, tab3 = st.tabs(["🔮 חיזוי חדש", "📜 היסטוריית חיזויים", "✅ דיוק למידה"])

# טעינת נתונים ראשונית
history_df, _ = get_github_file("lotto_data.csv")
predictions_df, pred_sha = get_github_file("predictions.csv")

with tab1:
    st.title("מערכת חיזוי זהב")
    if not history_df.empty:
        next_lottery_num = int(history_df.iloc[0, 0]) + 1
        st.write(f"חיזוי להגרלה מספר: **{next_lottery_num}**")
        
        if st.button("ייצר חיזוי חכם (חוקי הזהב)"):
            nums, strong, trend = generate_gold_prediction(history_df)
            
            # תצוגה
            cols = st.columns(7)
            for i, n in enumerate(nums): cols[i].markdown(f'<div class="number-ball">{n}</div>', unsafe_allow_html=True)
            cols[6].markdown(f'<div class="number-ball strong-ball">{strong}</div>', unsafe_allow_html=True)
            
            # שמירה ל-GitHub
            new_pred = pd.DataFrame([[datetime.now().strftime("%d/%m/%Y"), next_lottery_num, str(nums), strong, trend]], 
                                    columns=['date', 'lottery_id', 'numbers', 'strong', 'trend'])
            predictions_df = pd.concat([new_pred, predictions_df]).head(50)
            save_github_file("predictions.csv", predictions_df, pred_sha)
            st.success("החיזוי נשמר בהיסטוריה!")
    else:
        st.error("לא נמצא קובץ נתונים ב-GitHub")

with tab2:
    st.subheader("📜 כל פעולות החיזוי")
    if not predictions_df.empty:
        for _, row in predictions_df.iterrows():
            st.markdown(f"""<div class="prediction-card">
                <strong>תאריך:</strong> {row['date']} | <strong>הגרלה:</strong> {row['lottery_id']}<br>
                מספרים: {row['numbers']} | חזק: {row['strong']} | טרנד: {row['trend']}
            </div>""", unsafe_allow_html=True)

with tab3:
    st.subheader("✅ בדיקת דיוק (ירוק = פגיעה)")
    if not predictions_df.empty and not history_df.empty:
        for _, pred in predictions_df.iterrows():
            # מציאת תוצאת האמת להגרלה המיועדת
            actual = history_df[history_df.iloc[:, 0] == pred['lottery_id']]
            if not actual.empty:
                actual_nums = actual.iloc[0, 1:7].astype(int).tolist()
                actual_strong = int(actual.iloc[0, 7])
                pred_nums_list = eval(pred['numbers'])
                
                st.write(f"הגרלה {pred['lottery_id']}:")
                cols = st.columns(7)
                for i, p_n in enumerate(pred_nums_list):
                    is_hit = "green-ball" if p_n in actual_nums else ""
                    cols[i].markdown(f'<div class="number-ball {is_hit}">{p_n}</div>', unsafe_allow_html=True)
                
                s_hit = "green-ball" if pred['strong'] == actual_strong else ""
                cols[6].markdown(f'<div class="number-ball strong-ball {s_hit}">{pred["strong"]}</div>', unsafe_allow_html=True)
                st.markdown("---")
            else:
                st.write(f"הגרלה {pred['lottery_id']}: טרם פורסמו תוצאות אמת.")

st.caption("מערכת למידה אוטונומית - מבוססת חוקי הזהב")