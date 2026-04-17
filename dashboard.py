import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import grade5_data as g5
import grade8_data as g8

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
    .student-metric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ddd;
        text-align: center;
        margin-bottom: 15px;
    }
    .student-metric h4 { margin: 0; color: #6c757d; font-size: 14px; }
    .student-metric .value { font-size: 24px; font-weight: bold; color: #1a1a1a; margin-top: 5px; }
    .student-metric .percentile { font-size: 14px; color: #007bff; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# Path to the data folder
ASSET_DIR = "Asset"

# Mapping subjects to codes used in filenames
SUBJECT_MAP = {
    "English": "eng", "Hindi": "hindi", "Maths": "mat", "Science": "sci", "Social Studies": "sst"
}

# --- Data Loading Functions ---

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

@st.cache_data
def load_comparison_data():
    path_bench = os.path.join(ASSET_DIR, "skill benchmarking.csv")
    path_comp_skill = os.path.join(ASSET_DIR, "skill.csv")
    path_subject = os.path.join(ASSET_DIR, "subject.csv")
    
    df_bench = pd.read_csv(path_bench) if os.path.exists(path_bench) else pd.DataFrame()
    df_skill = pd.read_csv(path_comp_skill) if os.path.exists(path_comp_skill) else pd.DataFrame()
    df_sub = pd.read_csv(path_subject) if os.path.exists(path_subject) else pd.DataFrame()
    
    return df_bench, df_skill, df_sub

@st.cache_data
def load_average_data():
    path = os.path.join(ASSET_DIR, "average data.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = [c.replace('\ufeff', '').strip() for c in df.columns]
        return df
    return pd.DataFrame()

# --- Initialize Data ---
yoy_df = load_yoy_data()
question_df = load_question_data()
df_bench, df_comp_skill, df_sub = load_comparison_data()
avg_data_df = load_average_data()

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
tab_birdseye, tab_skills, tab_yoy, tab_comparisons, tab_misconceptions, tab_student = st.tabs([
    "🦅 Bird's-Eye View", 
    "🎯 Skill Deep Dive", 
    "📉 YoY Trends", 
    "⚖️ Comparisons",
    "🛑 Misconception Analysis",
    "👤 Student Analysis"
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

        st.markdown(f'<div class="section-header">Student Profiles: Collective Average Comparison (Grade {selected_grade})</div>', unsafe_allow_html=True)
        current_data = g5.STUDENT_DATA if selected_grade == 5 else g8.STUDENT_DATA
        avg_student_metrics = []
        if current_data:
            for sub in SUBJECT_MAP.keys():
                pct_scores = [info[sub]['Percentile'] for info in current_data.values() if sub in info and 'Percentile' in info[sub]]
                if pct_scores:
                    avg_student_metrics.append({
                        "Subject": sub, 
                        "Average Percentile": sum(pct_scores)/len(pct_scores),
                    })
            
            df_avg_student = pd.DataFrame(avg_student_metrics)
            if not df_avg_student.empty:
                c3, c4 = st.columns(2)
                with c3:
                    fig_avg_bar = px.bar(df_avg_student, x='Subject', y='Average Percentile', color='Subject',
                                        title=f"Sample Students: Avg Percentile", text_auto='.1f')
                    fig_avg_bar.update_layout(yaxis_range=[0,100], showlegend=False)
                    st.plotly_chart(fig_avg_bar, use_container_width=True)
                with c4:
                    # Filter average data for the selected grade
                    class_avg_data = pd.DataFrame()
                    if not avg_data_df.empty:
                        class_avg_data = avg_data_df[avg_data_df['Class'] == selected_grade]
                        val_col = 'Vasant Valley School (2025)'
                        if val_col in class_avg_data.columns:
                            class_avg_data = class_avg_data[['Subject', val_col]].rename(columns={val_col: 'Overall Average'})
                    
                    if not class_avg_data.empty:
                        merged_comp = pd.merge(class_avg_data, df_avg_student, on="Subject", how="inner")
                    else:
                        merged_comp = df_avg_student.copy()
                        merged_comp['Overall Average'] = 0
                        
                    fig_comp = go.Figure()
                    fig_comp.add_trace(go.Bar(x=merged_comp['Subject'], y=merged_comp['Overall Average'], name='Overall School Score (2025)', yaxis='y', marker_color='#007bff'))
                    fig_comp.add_trace(go.Scatter(x=merged_comp['Subject'], y=merged_comp['Average Percentile'], name='Sample Avg Pctl', mode='lines+markers', yaxis='y', line=dict(color='#dc3545', width=3)))
                    fig_comp.update_layout(
                        title="Overall School Score vs Sample Student Percentile",
                        yaxis=dict(title="Score / Percentile", range=[0, 100]),
                        barmode='group'
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)
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
    st.markdown(f'<div class="section-header">Historical Growth: All Subjects (Grade {selected_grade})</div>', unsafe_allow_html=True)
    if not yoy_df.empty:
        sub_yoy = yoy_df[yoy_df.iloc[:, 0].str.contains(str(selected_grade), na=False)]
        if not sub_yoy.empty:
            trend = sub_yoy.melt(id_vars=['Subject'], value_vars=['2022 [W]', '2023 [W]', '2024 [W]', '2025 [W]'], 
                                var_name='Year', value_name='Score')
            trend['Year'] = trend['Year'].str.extract('(\d+)').astype(int)
            fig_trend = px.line(trend, x='Year', y='Score', color='Subject', markers=True)
            fig_trend.update_layout(xaxis=dict(tickmode='linear'))
            st.plotly_chart(fig_trend, use_container_width=True)

# TAB 4: COMPARISONS
with tab_comparisons:
    st.markdown('<div class="section-header">School Performance Comparisons (Grade 5 & 8 Side-by-Side)</div>', unsafe_allow_html=True)
    
    col5, col8 = st.columns(2)
    
    for col, g_val in zip([col5, col8], [5, 8]):
        with col:
            st.markdown(f"<h3 style='text-align: center; color: #007bff;'>Grade {g_val} Performance</h3>", unsafe_allow_html=True)
            
            st.markdown(f"#### Subject Growth (2022 - 2025)")
            if not df_sub.empty:
                sub_data = df_sub[df_sub['Class'] == g_val]
                if not sub_data.empty:
                    sub_trend = sub_data.melt(id_vars=['Subject'], value_vars=['2022', '2023', '2024', '2025'], 
                                              var_name='Year', value_name='Score')
                    fig_sub_trend = px.line(sub_trend, x='Year', y='Score', color='Subject', markers=True)
                    st.plotly_chart(fig_sub_trend, use_container_width=True)
                else:
                    st.info(f"No subject trend data found for Grade {g_val}.")
                    
            st.markdown(f"#### Skill Benchmarking (2024 vs 2025)")
            if not df_bench.empty:
                bench_data = df_bench[df_bench['Class'] == g_val]
                if not bench_data.empty:
                    fig_bench = go.Figure()
                    fig_bench.add_trace(go.Bar(x=bench_data['Subject'], y=bench_data['Vasant Valley School (New Delhi) (2024)'], name='2024', marker_color='#ced4da'))
                    fig_bench.add_trace(go.Bar(x=bench_data['Subject'], y=bench_data['Vasant Valley School (New Delhi) (2025)'], name='2025', marker_color='#007bff'))
                    fig_bench.update_layout(barmode='group')
                    st.plotly_chart(fig_bench, use_container_width=True)
                else:
                    st.info(f"No skill benchmarking data found for Grade {g_val}.")

            st.markdown("#### Micro-Skill vs National Average")
            if not df_comp_skill.empty:
                comp_skill_data = df_comp_skill[df_comp_skill['CLASS'] == g_val]
                if not comp_skill_data.empty:
                    fig_comp_skill = go.Figure()
                    fig_comp_skill.add_trace(go.Bar(y=comp_skill_data['SKILL_NAME'], x=comp_skill_data['Vasant Valley School, New Delhi'], name='School', orientation='h', marker_color='#28a745'))
                    fig_comp_skill.add_trace(go.Bar(y=comp_skill_data['SKILL_NAME'], x=comp_skill_data['National Average'], name='National', orientation='h', marker_color='#ffc107'))
                    fig_comp_skill.update_layout(barmode='group', height=400)
                    st.plotly_chart(fig_comp_skill, use_container_width=True)
                else:
                    st.info(f"No micro-skill comparison data found for Grade {g_val}.")

# TAB 5: MISCONCEPTIONS & QUESTION ANALYSIS
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

# TAB 6: STUDENT ANALYSIS
with tab_student:
    st.markdown(f'<div class="section-header">Student Performance Analysis - Grade {selected_grade}</div>', unsafe_allow_html=True)
    
    # Load correct dataset based on grade
    current_data = g5.STUDENT_DATA if selected_grade == 5 else g8.STUDENT_DATA
    
    if current_data:
        # Comparative Case Study
        st.markdown(f"#### 🌐 Comparative Case Study: All Grade {selected_grade} Students")
        all_students_data = []
        for name, info in current_data.items():
            row = {"Student": name}
            for sub in SUBJECT_MAP.keys():
                row[sub] = info.get(sub, {}).get("Percentile", None)
            all_students_data.append(row)
        
        df_all_students = pd.DataFrame(all_students_data)
        
        if not df_all_students.empty:
            df_melted = df_all_students.melt(id_vars=["Student"], var_name="Subject", value_name="Percentile")
            fig_all = px.bar(df_melted, x="Student", y="Percentile", color="Subject", 
                             barmode="group", title=f"All-Student Comparison (Percentiles)",
                             height=500)
            st.plotly_chart(fig_all, use_container_width=True)
            
            with st.expander("📄 View Underlying Data (Percentiles)"):
                st.dataframe(df_all_students, use_container_width=True)
        
        st.markdown("---")
        st.markdown(f"#### 👤 Individual Learner Profile")
        
        student_list = list(current_data.keys())
        selected_student = st.selectbox("Select Student / Profile:", student_list)
        
        student_info = current_data[selected_student]
        
        st.markdown(f"#### Performance Overview: {selected_student}")
        
        c1, c2 = st.columns([1, 2])
        
        # Radar Chart for Percentiles
        radar_df = pd.DataFrame([{
            "Subject": sub, "Percentile": metrics.get("Percentile", 0)
        } for sub, metrics in student_info.items()])
        
        with c1:
            if not radar_df.empty:
                fig_student_radar = px.line_polar(
                    radar_df, r='Percentile', theta='Subject', line_close=True,
                    title="Student Percentile Radar", range_r=[0, 100]
                )
                fig_student_radar.update_traces(fill='toself', marker_color='#6c5ce7')
                st.plotly_chart(fig_student_radar, use_container_width=True)
                
        with c2:
            st.markdown("##### Subject Details")
            cols = st.columns(3)
            i = 0
            for sub, metrics in student_info.items():
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="student-metric">
                        <h4>{sub}</h4>
                        <div class="value">{metrics.get('Raw', '-')}/{metrics.get('Total', '-')}</div>
                        <div class="percentile">{metrics.get('Percentile', 0)}th Percentile</div>
                        <div style="font-size: 12px; color: #888;">Scaled: {metrics.get('Scaled', '-')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                i += 1
                
        # Show specific subject details if available
        if selected_subject in student_info:
            sub_metrics = student_info[selected_subject]
            st.info(f"**Insight:** This student is currently scoring in the **{sub_metrics.get('Percentile', 0)}th percentile** in {selected_subject} nationally.")
            
        # Optional: Expandable Answer Keys block (Since answers were only provided for Grade 5 in the prompt, apply condition)
        if selected_grade == 5 and hasattr(g5, 'ANSWER_KEYS'):
            with st.expander("📝 View Grade 5 Official Answer Keys"):
                for subject, key in g5.ANSWER_KEYS.items():
                    st.markdown(f"**{subject}**: `{key}`")
    else:
        st.warning(f"No student profile data available for Grade {selected_grade}.")

st.sidebar.markdown("---")
st.sidebar.success("✅ Dashboard successfully upgraded with Performance Capabilities.")