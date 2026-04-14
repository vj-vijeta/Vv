import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page configuration
st.set_page_config(
    page_title="Vasant Valley - Asset Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); border: 1px solid #e9ecef;
        text-align: center; margin-bottom: 20px;
    }
    .section-header {
        font-size: 24px; font-weight: 700; color: #1a1a1a;
        margin-top: 30px; margin-bottom: 20px;
        border-bottom: 2px solid #007bff; padding-bottom: 8px;
    }
    .question-card {
        background-color: #ffffff; padding: 25px; border-radius: 10px;
        border-left: 6px solid #ffc107; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .explanation-box {
        background-color: #e9ecef; padding: 15px; border-radius: 8px;
        margin-top: 15px; font-size: 14px;
    }
    .skill-card { padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid; }
    .best-skill { background-color: #e6ffed; border-left-color: #28a745; }
    .worst-skill { background-color: #fff5f5; border-left-color: #dc3545; }
    </style>
""", unsafe_allow_html=True)

<<<<<<< HEAD
# Path to data
ASSET_DIR = os.path.join(os.path.dirname(__file__), "Asset")
=======
# Path to the data folder
ASSET_DIR = "Asset"

# Mapping subjects to codes used in filenames
SUBJECT_MAP = {
    "English": "eng", "Hindi": "hindi", "Maths": "mat", "Science": "sci", "Social Studies": "sst"
}

# --- Data Loading Functions ---
>>>>>>> 7f3c811 (refactor: update ASSET_DIR to use relative path instead of absolute path)

@st.cache_data
def load_yoy_data():
    yoy_frames = []
    for sub, code in SUBJECT_MAP.items():
        # Adjusting 'mat' to 'math' for YoY filenames
        file_code = "math" if code == "mat" else code
        filename = f"yoy-{file_code}.csv"
        path = os.path.join(ASSET_DIR, filename)
        
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Remove BOM and whitespace from column names
            df.columns = [c.replace('\ufeff', '').strip() for c in df.columns]
            df['Subject'] = sub
            yoy_frames.append(df)
            
    if not yoy_frames:
        return pd.DataFrame()
    return pd.concat(yoy_frames, ignore_index=True)

@st.cache_data
def load_skill_data(subject_code):
    filename = f"Skill Performance -{subject_code}.csv"
    path = os.path.join(ASSET_DIR, filename)
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = [c.replace('\ufeff', '').strip() for c in df.columns]
        return df
    return pd.DataFrame()

@st.cache_data
def load_question_data():
    path = os.path.join(ASSET_DIR, "Misconceptions.csv")
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            return df.fillna("Data not available")
        except Exception as e:
            st.error(f"Error reading Misconceptions.csv: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# --- Initialize Data ---
yoy_df = load_yoy_data()
question_df = load_question_data()

# --- Sidebar Controls ---
st.sidebar.image("https://ei.study/wp-content/uploads/2022/10/edilogo.png", width=60)
st.sidebar.markdown("---")
st.sidebar.image("https://www.vasantvalley.org/wp-content/themes/vasant/images/logo-vasant-valley.svg", width=100)

st.sidebar.title("Configuration")

available_classes = [5, 8]
selected_grade = st.sidebar.radio("Select Grade", available_classes)
selected_subject = st.sidebar.selectbox("Select Subject", list(SUBJECT_MAP.keys()))

# --- Header ---
st.title("📊 Comprehensive Asset Performance Dashboard")
st.markdown(f"### Vasant Valley School | Grade {selected_grade} | {selected_subject}")

# --- Tabs ---
tab_birdseye, tab_skills, tab_yoy, tab_misconceptions = st.tabs([
    "🦅 Bird's-Eye View", 
    "🎯 Skill Deep Dive", 
    "📉 YoY Trends", 
    "🛑 Misconception Analysis"
])

# TAB 1: BIRD'S-EYE VIEW
with tab_birdseye:
    st.markdown(f'<div class="section-header">Overall Grade {selected_grade} Performance</div>', unsafe_allow_html=True)
    if not yoy_df.empty:
        # Filtering for the specific grade (e.g., 'Class 5')
        grade_data = yoy_df[yoy_df.iloc[:, 0].str.contains(str(selected_grade), na=False)]
        
        cols = st.columns(len(SUBJECT_MAP))
        for i, sub_name in enumerate(SUBJECT_MAP.keys()):
            sub_data = grade_data[grade_data['Subject'] == sub_name]
            if not sub_data.empty:
                latest = sub_data['2025 [W]'].values[0]
                prev = sub_data['2024 [W]'].values[0]
                with cols[i]:
                    st.metric(label=sub_name, value=f"{latest:.1f}", delta=f"{latest-prev:.1f} vs '24")

        c1, c2 = st.columns(2)
        with c1:
            fig_bar = px.bar(grade_data, x='Subject', y='2025 [W]', color='Subject', 
                             title="2025 Performance by Subject",
                             labels={'2025 [W]': 'Score'})
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            fig_radar = px.line_polar(grade_data, r='2025 [W]', theta='Subject', line_close=True,
                                      title="Grade Balance Radar")
            fig_radar.update_traces(fill='toself')
            st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.error(f"No YoY data files found in the '{ASSET_DIR}' folder.")

# TAB 2: SKILL DEEP DIVE
with tab_skills:
    st.markdown(f'<div class="section-header">Skill Benchmarking: {selected_subject}</div>', unsafe_allow_html=True)
    skill_df = load_skill_data(SUBJECT_MAP[selected_subject])
    if not skill_df.empty:
        g_skill = skill_df[skill_df['CLASS'] == selected_grade]
        school_col = "Vasant Valley School, New Delhi"
        nat_col = "National Average"
        
        if not g_skill.empty:
            g_skill = g_skill.sort_values(by=school_col, ascending=False)
            s1, s2 = st.columns(2)
            with s1:
                st.markdown("#### 🌟 Top Performing Skills")
                for _, row in g_skill.head(3).iterrows():
                    st.markdown(f'<div class="skill-card best-skill"><strong>{row["SKILL_NAME"]}</strong><br/>School: {row[school_col]:.1f}% | National: {row[nat_col]:.1f}%</div>', unsafe_allow_html=True)
            with s2:
                st.markdown("#### ⚠️ Skills Needing Attention")
                for _, row in g_skill.tail(3).iloc[::-1].iterrows():
                    st.markdown(f'<div class="skill-card worst-skill"><strong>{row["SKILL_NAME"]}</strong><br/>School: {row[school_col]:.1f}% | National: {row[nat_col]:.1f}%</div>', unsafe_allow_html=True)
            
            fig_skills = go.Figure()
            fig_skills.add_trace(go.Bar(y=g_skill['SKILL_NAME'], x=g_skill[school_col], name='School', orientation='h', marker_color='#007bff'))
            fig_skills.add_trace(go.Bar(y=g_skill['SKILL_NAME'], x=g_skill[nat_col], name='National', orientation='h', marker_color='#ced4da'))
            fig_skills.update_layout(barmode='group', height=500)
            st.plotly_chart(fig_skills, use_container_width=True)
        else:
            st.info(f"No Grade {selected_grade} data in the skill report for {selected_subject}.")

# TAB 3: HISTORICAL TRENDS
with tab_yoy:
    st.markdown(f'<div class="section-header">Historical Growth: {selected_subject}</div>', unsafe_allow_html=True)
    if not yoy_df.empty:
        sub_yoy = yoy_df[(yoy_df.iloc[:, 0].str.contains(str(selected_grade), na=False)) & (yoy_df['Subject'] == selected_subject)]
        if not sub_yoy.empty:
            trend = sub_yoy.melt(id_vars=['Subject'], value_vars=['2022 [W]', '2023 [W]', '2024 [W]', '2025 [W]'], 
                                var_name='Year', value_name='Score')
            trend['Year'] = trend['Year'].str.extract('(\d+)').astype(int)
            fig_trend = px.line(trend, x='Year', y='Score', markers=True, text='Score')
            fig_trend.update_layout(xaxis=dict(tickmode='linear'))
            st.plotly_chart(fig_trend, use_container_width=True)

# ==========================================
# TAB 4: MISCONCEPTIONS & QUESTION ANALYSIS
# ==========================================
with tab_misconceptions:
    st.markdown('<div class="section-header">Diagnostic Analysis: Questions & Misconceptions</div>', unsafe_allow_html=True)
    
    if not question_df.empty:
        # Filter by Grade and Subject
        q_filtered = question_df[
            (question_df['Grade'] == selected_grade) & 
            (question_df['Subject'] == selected_subject)
        ]
        
        # Add a Year Filter inside the tab
        available_years = sorted(q_filtered['Year'].unique().tolist(), reverse=True)
        selected_year = st.selectbox("Select Academic Year", available_years) if available_years else None
        
        final_q = q_filtered[q_filtered['Year'] == selected_year] if selected_year else q_filtered

        if not final_q.empty:
            for _, row in final_q.iterrows():
                # Determine if it's "Low Performing" (School < National)
                is_low = float(row['School_Performance'].strip('%')) < float(row['National_Performance'].strip('%'))
                border_color = "#dc3545" if is_low else "#ffc107"
                status_label = "⚠️ Low Performing" if is_low else "🔍 Misconception"

                options_formatted = row['Options'].replace('\\n', '<br/>')
                st.markdown(f"""
                <div class="question-card" style="border-left-color: {border_color};">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: bold; color: {border_color};">{status_label}</span>
                        <span style="color: #6c757d; font-size: 0.9em;">Skill: {row['Tested_Skill']}</span>
                    </div>
                    <p style="font-size: 18px; font-weight: 600; margin-top: 10px;">Q: {row['Question']}</p>
                    <div style="background-color: #f8f9fa; padding: 12px; border-radius: 5px; margin-bottom: 15px; font-family: sans-serif; border: 1px solid #eee;">
                        {options_formatted}
                    </div>
                    <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                        <div style="background: #e6ffed; padding: 5px 12px; border-radius: 4px; border: 1px solid #28a745; color: #1e7e34;">Correct: <b>{row['Correct_Answer']}</b></div>
                        <div style="background: #f8f9fa; padding: 5px 12px; border-radius: 4px; border: 1px solid #ddd;">School: <b>{row['School_Performance']}</b></div>
                        <div style="background: #f8f9fa; padding: 5px 12px; border-radius: 4px; border: 1px solid #ddd;">National: <b>{row['National_Performance']}</b></div>
                    </div>
                    <div class="explanation-box" style="border-top: 2px solid {border_color};">
                        <strong>Teacher Insight:</strong> {row['Explanation']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"No specific records found for {selected_subject} in {selected_year}.")
    else:
        st.warning("Please ensure 'Misconceptions.csv' is uploaded to view question-level diagnostics.")
st.sidebar.markdown("---")
st.sidebar.success("✅ Dashboard successfully upgraded with Question-Level Diagnostics.")