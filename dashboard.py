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
    .metric-label {
        font-size: 14px;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 28px;
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
    .grade-badge {
        background-color: #007bff;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 16px;
        font-weight: 600;
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
ASSET_DIR = "/Users/vijeta/Downloads/vasanth valley/Asset"

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

# --- Sidebar ---
st.sidebar.image("https://www.vasantvalley.org/vasantvalley/images/logo.png", width=150)
st.sidebar.title("Global Filters")

student_df = load_student_data()

if student_df is not None:
    # Cleanup column names
    student_df.columns = [c.replace('\ufeff', '') for c in student_df.columns]
    
    subjects = sorted(student_df['Subject'].unique().tolist())
    selected_subject = st.sidebar.selectbox("Select Subject", subjects, index=0)
    
    classes = sorted(student_df['Class'].unique().tolist())
    selected_classes = st.sidebar.multiselect("Select Grades (Classes)", classes, default=classes)
    
    # Filter data globally for the subject
    df_subject = student_df[student_df['Subject'] == selected_subject]
    df_filtered = df_subject[df_subject['Class'].isin(selected_classes)]
else:
    st.error("Could not load student data. Please check the 'Asset' directory.")
    st.stop()

# --- Main Dashboard ---
st.title("📊 Asset Performance Dashboard")
st.markdown(f"### Vasant Valley School | {selected_subject} - Winter 2025")

# Create Tabs
tab_overview, tab_grades = st.tabs(["🏛️ School Overview", "🎓 Grade-wise Reports"])

with tab_overview:
    st.markdown('<div class="section-header">Aggregated Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Students</div><div class="metric-value">{len(df_filtered['Name'].unique())}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Raw Score</div><div class="metric-value">{df_filtered['Raw Score'].mean():.1f}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Percentile</div><div class="metric-value">{df_filtered['Percentile'].mean():.1f}</div></div>""", unsafe_allow_html=True)
    with col4:
        toppers = len(df_filtered[df_filtered['Class Subject Topper'] == 'Yes'])
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Subject Toppers</div><div class="metric-value">{toppers}</div></div>""", unsafe_allow_html=True)

    # Usage Row
    u_col1, u_col2 = st.columns(2)
    with u_col1:
        fig_part = px.bar(
            df_filtered.groupby('Class').size().reset_index(name='Count'),
            x='Class', y='Count', title='Participation by Grade',
            color='Class', color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_part, use_container_width=True)
    with u_col2:
        fig_dist = px.box(
            df_filtered, x='Class', y='Percentile', title='Percentile Distribution by Grade',
            color='Class'
        )
        st.plotly_chart(fig_dist, use_container_width=True)

with tab_grades:
    if not selected_classes:
        st.warning("Please select at least one grade in the sidebar.")
    else:
        for grade in selected_classes:
            st.markdown(f'<div class="section-header">Grade {grade} - {selected_subject}</div>', unsafe_allow_html=True)
            
            grade_df = df_filtered[df_filtered['Class'] == grade]
            
            # Grade Metrics
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Students</div><div class="metric-value">{len(grade_df)}</div></div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Raw</div><div class="metric-value">{grade_df['Raw Score'].mean():.1f}</div></div>""", unsafe_allow_html=True)
            with m3:
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Percentile</div><div class="metric-value">{grade_df['Percentile'].mean():.1f}</div></div>""", unsafe_allow_html=True)
            with m4:
                g_toppers = len(grade_df[grade_df['Class Subject Topper'] == 'Yes'])
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Toppers</div><div class="metric-value">{g_toppers}</div></div>""", unsafe_allow_html=True)

            # Skill Performance for this Grade
            skill_code = SUBJECT_MAP.get(selected_subject)
            skill_df = load_skill_data(skill_code)
            
            if skill_df is not None:
                skill_df.columns = [c.replace('\ufeff', '') for c in skill_df.columns]
                # Filter by Class correctly (Skill files use CLASS column)
                g_skill_df = skill_df[skill_df['CLASS'] == grade]
                
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
                    
                    # Grade-wise comparison bar chart
                    fig_comp = go.Figure()
                    fig_comp.add_trace(go.Bar(
                        y=g_skill_df['SKILL_NAME'], x=g_skill_df[school_col],
                        name='Vasant Valley', orientation='h', marker_color='#007bff'
                    ))
                    fig_comp.add_trace(go.Bar(
                        y=g_skill_df['SKILL_NAME'], x=g_skill_df[nat_col],
                        name='National Average', orientation='h', marker_color='#ced4da'
                    ))
                    fig_comp.update_layout(barmode='group', height=400, margin=dict(l=20, r=20, t=30, b=20),
                                         title=f"Skill Benchmarking - Grade {grade}")
                    st.plotly_chart(fig_comp, use_container_width=True)
                else:
                    st.info(f"Detailed skill performance data for Grade {grade} is not available in the report.")
            else:
                st.warning(f"Skill report for {selected_subject} missing.")
            
            st.divider()

st.sidebar.markdown("---")
st.sidebar.info("Data source: Ei ASSET Winter 2025 Reports")
st.sidebar.markdown("Separate reports are generated for each selected grade in the 'Grade-wise Reports' tab.")
