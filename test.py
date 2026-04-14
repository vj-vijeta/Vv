import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- Configuration & Paths ---
ASSET_DIR = "Asset"
SUBJECT_MAP = {
    "English": "eng", "Hindi": "hindi", "Maths": "mat", "Science": "sci", "Social Studies": "sst"
}

# --- Data Loading Functions ---

@st.cache_data
def load_yoy_data():
    yoy_frames = []
    for sub, code in SUBJECT_MAP.items():
        # Maps 'mat' to 'math' for YoY files if needed
        file_code = "math" if code == "mat" else code
        path = os.path.join(ASSET_DIR, f"yoy-{file_code}.csv")
        
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = [c.replace('\ufeff', '').strip() for c in df.columns]
            df['Subject'] = sub
            yoy_frames.append(df)
            
    return pd.concat(yoy_frames, ignore_index=True) if yoy_frames else pd.DataFrame()

@st.cache_data
def load_skill_data(subject_code):
    path = os.path.join(ASSET_DIR, f"Skill Performance -{subject_code}.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = [c.replace('\ufeff', '').strip() for c in df.columns]
        return df
    return pd.DataFrame()

@st.cache_data
def load_question_data():
    path = os.path.join(ASSET_DIR, "Misconceptions.csv")
    if os.path.exists(path):
        return pd.read_csv(path).fillna("N/A")
    return pd.DataFrame()

# --- Initialize Dashboard ---
st.set_page_config(page_title="Vasant Valley Dashboard", layout="wide")
yoy_df = load_yoy_data()
question_df = load_question_data()

# Sidebar
st.sidebar.title("Dashboard Controls")
selected_grade = st.sidebar.radio("Select Grade", [5, 8])
selected_subject = st.sidebar.selectbox("Select Subject", list(SUBJECT_MAP.keys()))

st.title(f"📊 Asset Performance: Grade {selected_grade}")

# --- Tab Layout ---
tab_birdseye, tab_skills, tab_misconceptions = st.tabs([
    "🦅 Bird's-Eye View (Grade Summary)", 
    "🎯 Skill Benchmarking & Trends", 
    "🛑 Misconception Analysis"
])

# ==========================================
# TAB 1: BIRD'S-EYE VIEW (Entire Grade)
# ==========================================
with tab_birdseye:
    st.header(f"Grade {selected_grade} Summary")
    if not yoy_df.empty:
        # Filter for selected grade across all subjects
        grade_summary = yoy_df[yoy_df.iloc[:, 0].str.contains(str(selected_grade), na=False)]
        
        # Performance Comparison: Latest Year
        fig_global = px.bar(grade_summary, x='Subject', y='2025 [W]', 
                           title="Current Year Performance Across All Subjects",
                           color='2025 [W]', color_continuous_scale='Blues')
        st.plotly_chart(fig_global, use_container_width=True)
        
        # Subject Progress: Current vs Previous
        grade_summary['Growth'] = grade_summary['2025 [W]'] - grade_summary['2024 [W]']
        st.subheader("Year-on-Year Growth by Subject")
        cols = st.columns(len(grade_summary))
        for idx, row in grade_summary.iterrows():
            with cols[list(grade_summary.index).index(idx)]:
                st.metric(label=row['Subject'], value=f"{row['2025 [W]']:.1f}", delta=f"{row['Growth']:.1f}")
    else:
        st.error("YoY data missing in Asset folder.")

# ==========================================
# TAB 2: SKILL BENCHMARKING (Subject Specific)
# ==========================================
with tab_skills:
    st.header(f"{selected_subject} Skill Analysis")
    
    col_l, col_r = st.columns(2)
    
    # Left: Current Skill Benchmarking (School vs National)
    with col_l:
        st.subheader("Current Skill Benchmarking (2025)")
        skill_df = load_skill_data(SUBJECT_MAP[selected_subject])
        if not skill_df.empty:
            g_skill = skill_df[skill_df['CLASS'] == selected_grade]
            if not g_skill.empty:
                fig_bench = go.Figure()
                fig_bench.add_trace(go.Bar(y=g_skill['SKILL_NAME'], x=g_skill['Vasant Valley School, New Delhi'], 
                                         name='School', orientation='h', marker_color='#007bff'))
                fig_bench.add_trace(go.Bar(y=g_skill['SKILL_NAME'], x=g_skill['National Average'], 
                                         name='National', orientation='h', marker_color='#ced4da'))
                fig_bench.update_layout(barmode='group', height=400, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_bench, use_container_width=True)
            else:
                st.info("No skill-level data for this grade.")
    
    # Right: Historical Subject Trend (Comparison with Previous Years)
    with col_r:
        st.subheader(f"{selected_subject} Growth Trend (2022-2025)")
        if not yoy_df.empty:
            sub_yoy = yoy_df[(yoy_df.iloc[:, 0].str.contains(str(selected_grade), na=False)) & 
                            (yoy_df['Subject'] == selected_subject)]
            if not sub_yoy.empty:
                trend_data = sub_yoy.melt(id_vars=['Subject'], 
                                        value_vars=['2022 [W]', '2023 [W]', '2024 [W]', '2025 [W]'], 
                                        var_name='Year', value_name='Score')
                trend_data['Year'] = trend_data['Year'].str.extract('(\d+)').astype(int)
                
                fig_trend = px.line(trend_data, x='Year', y='Score', markers=True, 
                                   title="Overall Subject Progress Over Years")
                fig_trend.update_layout(height=400)
                st.plotly_chart(fig_trend, use_container_width=True)

# ==========================================
# TAB 3: MISCONCEPTIONS
# ==========================================
with tab_misconceptions:
    st.header(f"Low Performing Questions: {selected_subject}")
    if not question_df.empty:
        q_filtered = question_df[(question_df['Grade'] == selected_grade) & 
                                (question_df['Subject'] == selected_subject)]
        
        if q_filtered.empty:
            st.info("No misconception data available for this selection.")
        else:
            for _, row in q_filtered.iterrows():
                with st.expander(f"Skill: {row['Tested_Skill']} (School: {row['School_Performance']} vs Nat: {row['National_Performance']})"):
                    st.write(f"**Question:** {row['Question']}")
                    st.code(row['Options'], language=None)
                    st.success(f"**Correct Answer:** {row['Correct_Answer']}")
                    st.info(f"**Explanation:** {row['Explanation']}")
    else:
        st.error("Misconceptions.csv not found in Asset folder.")