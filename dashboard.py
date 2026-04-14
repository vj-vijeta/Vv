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

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
        text-align: center;
        margin-bottom: 20px;
    }
    .subject-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-top: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .subject-card:hover {
        transform: translateY(-5px);
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 24px;
        color: #212529;
        font-weight: 700;
    }
    .section-header {
        font-size: 24px;
        font-weight: 700;
        color: #1a1a1a;
        margin-top: 30px;
        margin-bottom: 20px;
        border-bottom: 2px solid #007bff;
        padding-bottom: 8px;
    }
    .skill-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid;
    }
    .best-skill {
        background-color: #e6ffed;
        border-left-color: #28a745;
    }
    .worst-skill {
        background-color: #fff5f5;
        border-left-color: #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Path to data
ASSET_DIR = os.path.join(os.path.dirname(__file__), "Asset")

@st.cache_data
def load_student_data():
    path = os.path.join(ASSET_DIR, "Asset student data.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

@st.cache_data
def load_skill_data(subject_code):
    filename = f"Skill Performance -{subject_code}.csv"
    path = os.path.join(ASSET_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

# Mapping subjects to codes used in filenames
SUBJECT_MAP = {
    "English": "eng",
    "Hindi": "hindi",
    "Maths": "mat",
    "Science": "sci",
    "Social Studies": "sst"
}

# --- Load Data ---
student_df = load_student_data()
if student_df is not None:
    student_df.columns = [c.replace('\ufeff', '') for c in student_df.columns]
else:
    st.error("Could not load student data.")
    st.stop()

# --- Sidebar ---
st.sidebar.image("https://www.vasantvalley.org/vasantvalley/images/logo.png", width=150)
st.sidebar.title("Configuration")

# Global Grade Selection
classes = sorted(student_df['Class'].unique().tolist())
selected_grade = st.sidebar.selectbox("Select Grade (Class)", classes, index=0)

# --- Main Dashboard ---
st.title("📊 Asset Performance Dashboard")
st.markdown(f"### Vasant Valley School | Grade {selected_grade} - Winter 2025")

# Create Tabs
tab_home, tab_analysis, tab_overview = st.tabs(["🏠 Grade Home", "🔍 Subject Analysis", "🏛️ School Overview"])

with tab_home:
    st.markdown('<div class="section-header">Subject-wise Summary for Grade ' + str(selected_grade) + '</div>', unsafe_allow_html=True)
    
    grade_df = student_df[student_df['Class'] == selected_grade]
    subjects = sorted(grade_df['Subject'].unique().tolist())
    
    cols = st.columns(3)
    for i, subject in enumerate(subjects):
        with cols[i % 3]:
            sub_df = grade_df[grade_df['Subject'] == subject]
            avg_score = sub_df['Raw Score'].mean()
            avg_perc = sub_df['Percentile'].mean()
            toppers = len(sub_df[sub_df['Class Subject Topper'] == 'Yes'])
            
            st.markdown(f"""
                <div class="subject-card">
                    <h4 style="margin-top:0; color:#007bff;">{subject}</h4>
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <div>
                            <span style="font-size:12px; color:#6c757d;">AVG SCORE</span><br/>
                            <span style="font-size:20px; font-weight:700;">{avg_score:.1f}</span>
                        </div>
                        <div>
                            <span style="font-size:12px; color:#6c757d;">PERCENTILE</span><br/>
                            <span style="font-size:20px; font-weight:700;">{avg_perc:.1f}</span>
                        </div>
                    </div>
                    <div style="font-size:14px; color:#28a745; font-weight:600;">
                        🏆 {toppers} Subject Toppers
                    </div>
                </div>
                <br/>
            """, unsafe_allow_html=True)

    # Cross-Subject Comparison Chart
    st.markdown("#### Subject Comparison")
    sub_metrics = grade_df.groupby('Subject').agg({
        'Raw Score': 'mean',
        'Percentile': 'mean'
    }).reset_index()
    
    fig_home = px.bar(
        sub_metrics, x='Subject', y='Percentile', 
        title='Average Percentile across Subjects',
        color='Subject', color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_home.update_layout(showlegend=False)
    st.plotly_chart(fig_home, use_container_width=True)

with tab_analysis:
    st.markdown('<div class="section-header">Detailed Subject Analysis</div>', unsafe_allow_html=True)
    
    analysis_subject = st.selectbox("Select Subject for Deep Dive", subjects)
    
    # Analysis Filters
    df_analysis = grade_df[grade_df['Subject'] == analysis_subject]
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Students</div><div class="metric-value">{len(df_analysis)}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Raw</div><div class="metric-value">{df_analysis['Raw Score'].mean():.1f}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Percentile</div><div class="metric-value">{df_analysis['Percentile'].mean():.1f}</div></div>""", unsafe_allow_html=True)
    with col4:
        a_toppers = len(df_analysis[df_analysis['Class Subject Topper'] == 'Yes'])
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Toppers</div><div class="metric-value">{a_toppers}</div></div>""", unsafe_allow_html=True)

    # Skill Performance
    skill_code = SUBJECT_MAP.get(analysis_subject)
    skill_df = load_skill_data(skill_code)
    
    if skill_df is not None:
        skill_df.columns = [c.replace('\ufeff', '') for c in skill_df.columns]
        g_skill_df = skill_df[skill_df['CLASS'] == selected_grade]
        
        if not g_skill_df.empty:
            school_col = "Vasant Valley School, New Delhi"
            nat_col = "National Average"
            g_skill_df = g_skill_df.sort_values(by=school_col, ascending=False)
            
            s1, s2 = st.columns(2)
            with s1:
                st.markdown("#### Top Performing Skills")
                for _, row in g_skill_df.head(3).iterrows():
                    st.markdown(f"""<div class="skill-card best-skill">
                        <strong>{row['SKILL_NAME']}</strong><br/>
                        School: {row[school_col]:.1f}% | National: {row[nat_col]:.1f}%
                    </div>""", unsafe_allow_html=True)
            with s2:
                st.markdown("#### Skills Needing Attention")
                for _, row in g_skill_df.tail(3).iloc[::-1].iterrows():
                    st.markdown(f"""<div class="skill-card worst-skill">
                        <strong>{row['SKILL_NAME']}</strong><br/>
                        School: {row[school_col]:.1f}% | National: {row[nat_col]:.1f}%
                    </div>""", unsafe_allow_html=True)
            
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(
                y=g_skill_df['SKILL_NAME'], x=g_skill_df[school_col],
                name='Vasant Valley', orientation='h', marker_color='#007bff'
            ))
            fig_comp.add_trace(go.Bar(
                y=g_skill_df['SKILL_NAME'], x=g_skill_df[nat_col],
                name='National Average', orientation='h', marker_color='#ced4da'
            ))
            fig_comp.update_layout(barmode='group', height=500, title=f"Skill Benchmarking - {analysis_subject}")
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info(f"Detailed skill data for Grade {selected_grade} is not available for {analysis_subject}.")
    else:
        st.warning("Skill report data missing.")

with tab_overview:
    st.markdown('<div class="section-header">School-wide Overview</div>', unsafe_allow_html=True)
    o_col1, o_col2 = st.columns(2)
    with o_col1:
        fig_part = px.bar(
            student_df.groupby(['Class', 'Subject']).size().reset_index(name='Count'),
            x='Class', y='Count', color='Subject', title='Total Participation - All Grades'
        )
        st.plotly_chart(fig_part, use_container_width=True)
    with o_col2:
        fig_trend = px.box(
            student_df, x='Subject', y='Percentile', color='Subject',
            title='Subject Proficiency Distribution (All Grades)'
        )
        st.plotly_chart(fig_trend, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("The 'Grade Home' tab provides a bird's-eye view of all subjects for your selected grade.")
