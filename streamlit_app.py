import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import io

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="COO Operational Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
    <style>
    .main { padding: 0px; }

    /* Objective Card */
    .objective-card {
        background: white;
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .objective-card:hover {
        border-color: #1e40af;
        box-shadow: 0 8px 16px rgba(30, 64, 175, 0.15);
        transform: translateY(-4px);
    }

    .objective-header {
        font-size: 18px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .objective-signal {
        font-size: 11px;
        color: #6b7280;
        font-style: italic;
        margin-bottom: 16px;
    }

    /* Sub-objective Box with inline sparkline */
    .subobjective-box {
        background: #f9fafb;
        border-left: 4px solid #1e40af;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 10px;
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 12px;
        align-items: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .subobjective-box:hover {
        background: #f3f4f6;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }

    .subobjective-box.cost { border-left-color: #ef4444; }
    .subobjective-box.quality { border-left-color: #059669; }
    .subobjective-box.efficiency { border-left-color: #f59e0b; }

    .subobjective-info {
        flex-grow: 1;
    }

    .subobjective-title {
        font-size: 12px;
        font-weight: 600;
        color: #1f2937;
    }

    .subobjective-value {
        font-size: 22px;
        font-weight: 700;
        color: #1e40af;
        margin: 8px 0;
    }

    .subobjective-trend {
        font-size: 11px;
        color: #6b7280;
    }

    .sparkline-container {
        width: 90px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Navigation buttons */
    .nav-container {
        display: flex;
        gap: 8px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }

    .nav-button {
        padding: 8px 14px;
        border-radius: 6px;
        border: 1px solid #d1d5db;
        background: white;
        cursor: pointer;
        font-size: 12px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .nav-button:hover {
        background: #f3f4f6;
        border-color: #1e40af;
    }

    .nav-button.active {
        background: #1e40af;
        color: white;
        border-color: #1e40af;
    }

    /* Trend indicator */
    .trend-up { color: #059669; font-weight: 600; }
    .trend-down { color: #ef4444; font-weight: 600; }
    .trend-neutral { color: #6b7280; font-weight: 600; }

    /* Detail Section */
    .detail-section {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }

    .detail-title {
        font-size: 16px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 15px;
    }

    /* KPI Card in detail */
    .kpi-detail-card {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }

    .kpi-detail-label {
        font-size: 12px;
        color: #6b7280;
        font-weight: 600;
    }

    .kpi-detail-value {
        font-size: 28px;
        font-weight: 700;
        color: #1e40af;
        margin: 8px 0;
    }

    .kpi-detail-trend {
        font-size: 11px;
        color: #6b7280;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== LOAD DATA ====================
@st.cache_data
def load_excel_data():
    try:
        excel_file = 'COO_ROI_Dashboard_KPIs_Complete_12.xlsx'
        
        data = {
            'Role_vs_Reality': pd.read_excel(excel_file, sheet_name='Role_vs_Reality_Analysis'),
            'Automation_ROI': pd.read_excel(excel_file, sheet_name='Automation_ROI_Potential'),
            'Digital_Index': pd.read_excel(excel_file, sheet_name='Digital_Workplace_Index'),
            'Process_Rework': pd.read_excel(excel_file, sheet_name='Process_Rework_Cost'),
            'FTR_Rate': pd.read_excel(excel_file, sheet_name='First_Time_Right_Rate'),
            'Adherence': pd.read_excel(excel_file, sheet_name='Process_Adherence_Rate'),
            'Resilience': pd.read_excel(excel_file, sheet_name='Operational_Resilience_Score'),
            'Escalation': pd.read_excel(excel_file, sheet_name='Escalation_Exception_Patterns'),
            'Capacity': pd.read_excel(excel_file, sheet_name='Hidden_Capacity_Burnout'),
            'Model_Accuracy': pd.read_excel(excel_file, sheet_name='Capacity_Model_Accuracy'),
            'Work_Models': pd.read_excel(excel_file, sheet_name='Work_Models_Effectiveness'),
            'Collaboration': pd.read_excel(excel_file, sheet_name='Collaboration_Overload'),
        }
        return data
    except FileNotFoundError:
        st.error("File not found: 'COO_ROI_Dashboard_KPIs_Complete_12.xlsx'")
        st.stop()

data = load_excel_data()

# ==================== SESSION STATE ====================
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'

# ==================== SIDEBAR FILTERS ====================
st.sidebar.markdown("## Filters")

role_months = sorted(data['Role_vs_Reality']['Month'].unique())
selected_months = st.sidebar.multiselect(
    "Select Months",
    role_months,
    default=list(role_months),
)

all_departments = sorted(
    list(set(list(data['Role_vs_Reality'].get('Department', []).unique()) + 
             list(data['Capacity'].get('Department', []).unique())))
)
selected_depts = st.sidebar.multiselect(
    "Select Departments",
    all_departments,
    default=all_departments,
)

dept_filter = selected_depts if len(selected_depts) > 0 else None

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ==================== HELPER FUNCTIONS ====================
def filter_data(df, month_col='Month', dept_col='Department'):
    result = df[df[month_col].isin(selected_months)]
    if dept_filter and dept_col in result.columns:
        result = result[result[dept_col].isin(dept_filter)]
    return result

def create_trend_chart(df, x_col, y_col, title, color='#1e40af'):
    """Create a trend line chart"""
    if len(df) < 2:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines+markers',
        line=dict(color=color, width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor=f'rgba(30, 64, 175, 0.1)'
    ))
    fig.update_layout(
        title=title,
        height=250,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode='x unified'
    )
    return fig

def create_sparkline(df, x_col, y_col, color='#1e40af'):
    """Create a compact sparkline chart for inline display"""
    if len(df) < 2:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines',
        line=dict(color=color, width=2.5),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15)',
        hoverinfo='y',
        hovertemplate='<b>%{y:.2f}</b><extra></extra>'
    ))
    fig.update_layout(
        title=None,
        height=40,
        width=90,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        hovermode='x'
    )
    return fig

def create_gauge_chart(value, max_value, title, color='#1e40af', size='medium'):
    """Create a gauge chart with configurable size"""
    height = 200 if size == 'small' else 250
    fig = go.Figure(data=[go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': '', 'font': {'size': 20}},
        title={'text': title, 'font': {'size': 14}},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, max_value], 'tickwidth': 2, 'ticklen': 8},
            'bar': {'color': color, 'thickness': 0.25},
            'steps': [
                {'range': [0, max_value*0.5], 'color': '#fee2e2'},
                {'range': [max_value*0.5, max_value*0.75], 'color': '#fef3c7'},
                {'range': [max_value*0.75, max_value], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    )])
    fig.update_layout(height=height, margin=dict(l=20, r=20, t=40, b=20), font=dict(size=11))
    return fig

def get_month_over_month_change(df, metric_col, month_col='Month'):
    """Calculate month-over-month change"""
    if len(df) < 2:
        return None, None
    
    df_sorted = df.sort_values(month_col)
    if len(df_sorted) < 2:
        return None, None
    
    last_value = df_sorted[metric_col].iloc[-1]
    prev_value = df_sorted[metric_col].iloc[-2]
    
    if prev_value == 0:
        change = 0
    else:
        change = ((last_value - prev_value) / abs(prev_value)) * 100
    
    return last_value, change

def round_value(value, metric_type='percentage'):
    """Round values intelligently based on metric type"""
    if metric_type == 'percentage':
        return round(value, 1)
    elif metric_type == 'decimal':
        return round(value, 3)
    elif metric_type == 'whole':
        return int(round(value, 0))
    elif metric_type == 'index':
        return round(value, 2)
    elif metric_type == 'currency':
        return round(value, 0)
    elif metric_type == 'hours':
        return round(value, 1)
    return round(value, 2)

def show_navigation():
    """Display navigation buttons"""
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("Home", key="btn_home", use_container_width=True):
            st.session_state.current_page = 'main'
            st.rerun()
    
    with col2:
        if st.button("Cost & Efficiency", key="btn_nav_cost", use_container_width=True):
            st.session_state.current_page = 'cost_efficiency'
            st.rerun()
    
    with col3:
        if st.button("Execution & Resilience", key="btn_nav_exec", use_container_width=True):
            st.session_state.current_page = 'execution_resilience'
            st.rerun()
    
    with col4:
        if st.button("Workforce & Productivity", key="btn_nav_workforce", use_container_width=True):
            st.session_state.current_page = 'workforce_productivity'
            st.rerun()

# ==================== HEADER ====================
st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); 
                color: white; padding: 30px 20px; border-radius: 0; 
                margin: -25px -20px 25px -20px; text-align: center;">
        <h1 style="margin: 0; font-size: 36px;">COO Operational Dashboard</h1>
        <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">Executive KPI Management with Visual Analytics</p>
    </div>
""", unsafe_allow_html=True)

# ==================== MAIN PAGE (L1) ====================
if st.session_state.current_page == 'main':
    st.markdown("### Key Objectives")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    # -------- OBJECTIVE 1: COST & EFFICIENCY --------
    with col1:
        rework_data = filter_data(data['Process_Rework'])
        auto_data = filter_data(data['Automation_ROI'])
        digital_data = filter_data(data['Digital_Index'])
        role_data = filter_data(data['Role_vs_Reality'])
        
        rework_pct = rework_data['Rework_Cost_Percentage'].mean() if len(rework_data) > 0 else 0
        auto_roi = auto_data['ROI_Percentage_6M'].mean() if len(auto_data) > 0 else 0
        automation_coverage = (auto_data.shape[0] / max(data['Automation_ROI'].shape[0], 1)) * 100
        friction = digital_data['Friction_Index_Score'].mean() if len(digital_data) > 0 else 0
        
        # Calculate MoM changes
        rework_val, rework_change = get_month_over_month_change(rework_data, 'Rework_Cost_Percentage')
        auto_val, auto_change = get_month_over_month_change(auto_data, 'ROI_Percentage_6M')
        friction_val, friction_change = get_month_over_month_change(digital_data, 'Friction_Index_Score')
        
        rework_trend = f"{round_value(rework_change, 'percentage'):+.1f}% vs last month" if rework_change is not None else "No data"
        auto_trend = f"{round_value(auto_change, 'percentage'):+.1f}% vs last month" if auto_change is not None else "No data"
        friction_trend = f"{round_value(friction_change, 'percentage'):+.1f}% vs last month" if friction_change is not None else "No data"
        
        if st.button("Cost & Efficiency", key="btn_cost", use_container_width=True, help="ROI, Rework, Automation, Digital Readiness"):
            st.session_state.current_page = 'cost_efficiency'
            st.rerun()
        
        st.markdown('<div class="objective-card"><div class="objective-signal">Monitor: ROI + Rework + Automation Coverage</div>', unsafe_allow_html=True)
        
        # Rework Cost
        chart_col_rework1, chart_col_rework2 = st.columns([3, 1], gap="small")
        with chart_col_rework1:
            st.markdown(f"""
            <div class="subobjective-box cost">
                <div class="subobjective-info">
                    <div class="subobjective-title">Rework Cost %</div>
                    <div class="subobjective-value">{round_value(rework_pct, 'percentage'):.1f}%</div>
                    <div class="subobjective-trend"><span class="trend-down">{rework_trend}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_rework2:
            if len(rework_data) > 1:
                rework_trend_data = rework_data.groupby('Month').agg({'Rework_Cost_Percentage': 'mean'}).reset_index().sort_values('Month')
                fig = create_sparkline(rework_trend_data, 'Month', 'Rework_Cost_Percentage', '#ef4444')
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Automation ROI
        chart_col_auto1, chart_col_auto2 = st.columns([3, 1], gap="small")
        with chart_col_auto1:
            st.markdown(f"""
            <div class="subobjective-box efficiency">
                <div class="subobjective-info">
                    <div class="subobjective-title">Automation ROI</div>
                    <div class="subobjective-value">{round_value(auto_roi, 'whole'):.0f}%</div>
                    <div class="subobjective-trend"><span class="trend-up">{auto_trend}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_auto2:
            if len(auto_data) > 1:
                auto_trend_data = auto_data.groupby('Month').agg({'ROI_Percentage_6M': 'mean'}).reset_index().sort_values('Month')
                fig = create_sparkline(auto_trend_data, 'Month', 'ROI_Percentage_6M', '#059669')
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Automation Coverage
        chart_col_cov1, chart_col_cov2 = st.columns([3, 1], gap="small")
        with chart_col_cov1:
            st.markdown(f"""
            <div class="subobjective-box efficiency">
                <div class="subobjective-info">
                    <div class="subobjective-title">Automation Coverage</div>
                    <div class="subobjective-value">{round_value(automation_coverage, 'percentage'):.0f}%</div>
                    <div class="subobjective-trend">Process automation</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_cov2:
            st.write("")
        
        # Digital Friction
        chart_col_fric1, chart_col_fric2 = st.columns([3, 1], gap="small")
        with chart_col_fric1:
            st.markdown(f"""
            <div class="subobjective-box efficiency">
                <div class="subobjective-info">
                    <div class="subobjective-value">{round_value(friction, 'index'):.1f}</div>
                    <div class="subobjective-trend"><span class="trend-down">{friction_trend}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_fric2:
            if len(digital_data) > 1:
                friction_trend_data = digital_data.groupby('Month').agg({'Friction_Index_Score': 'mean'}).reset_index().sort_values('Month')
                fig = create_sparkline(friction_trend_data, 'Month', 'Friction_Index_Score', '#f59e0b')
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # -------- OBJECTIVE 2: EXECUTION & RESILIENCE --------
    with col2:
        ftr_data = filter_data(data['FTR_Rate'])
        adherence_data = filter_data(data['Adherence'])
        resilience_data = filter_data(data['Resilience'])
        escalation_data = filter_data(data['Escalation'])
        
        ftr_rate = ftr_data['FTR_Rate_Percentage'].mean() if len(ftr_data) > 0 else 0
        adherence = adherence_data['Adherence_Rate_Percentage'].mean() if len(adherence_data) > 0 else 0
        resilience = resilience_data['Resilience_Score'].mean() if len(resilience_data) > 0 else 0
        escalations = escalation_data['Step_Exception_Count'].sum() if len(escalation_data) > 0 else 0
        
        # Calculate MoM changes
        ftr_val, ftr_change = get_month_over_month_change(ftr_data, 'FTR_Rate_Percentage')
        adh_val, adh_change = get_month_over_month_change(adherence_data, 'Adherence_Rate_Percentage')
        res_val, res_change = get_month_over_month_change(resilience_data, 'Resilience_Score')
        esc_val, esc_change = get_month_over_month_change(escalation_data, 'Step_Exception_Count')
        
        ftr_trend = f"{round_value(ftr_change, 'percentage'):+.1f}% vs last month" if ftr_change is not None else "No data"
        adh_trend = f"{round_value(adh_change, 'percentage'):+.1f}% vs last month" if adh_change is not None else "No data"
        res_trend = f"{round_value(res_change, 'percentage'):+.1f}% vs last month" if res_change is not None else "No data"
        esc_trend = f"{round_value(esc_change, 'percentage'):+.1f}% vs last month" if esc_change is not None else "No data"
        
        if st.button("Execution & Resilience", key="btn_execution", use_container_width=True, help="FTR, Adherence, Resilience, Exceptions"):
            st.session_state.current_page = 'execution_resilience'
            st.rerun()
        
        st.markdown('<div class="objective-card"><div class="objective-signal">Monitor: Quality + Reliability + Risk</div>', unsafe_allow_html=True)
        
        # FTR Rate
        chart_col_ftr1, chart_col_ftr2 = st.columns([3, 1], gap="small")
        with chart_col_ftr1:
            st.markdown(f"""
            <div class="subobjective-box quality">
                <div class="subobjective-info">
                    <div class="subobjective-value">{round_value(ftr_rate, 'percentage'):.1f}%</div>
                    <div class="subobjective-trend"><span class="trend-up">{ftr_trend}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_ftr2:
            if len(ftr_data) > 1:
                ftr_trend_data = ftr_data.groupby('Month').agg({'FTR_Rate_Percentage': 'mean'}).reset_index().sort_values('Month')
                fig = create_sparkline(ftr_trend_data, 'Month', 'FTR_Rate_Percentage', '#059669')
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Process Adherence
        chart_col_adh1, chart_col_adh2 = st.columns([3, 1], gap="small")
        with chart_col_adh1:
            st.markdown(f"""
            <div class="subobjective-box quality">
                <div class="subobjective-info">
                    <div class="subobjective-value">{round_value(adherence, 'percentage'):.1f}%</div>
                    <div class="subobjective-trend"><span class="trend-up">{adh_trend}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_adh2:
            if len(adherence_data) > 1:
                adh_trend_data = adherence_data.groupby('Month').agg({'Adherence_Rate_Percentage': 'mean'}).reset_index().sort_values('Month')
                fig = create_sparkline(adh_trend_data, 'Month', 'Adherence_Rate_Percentage', '#059669')
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Resilience Score
        chart_col_res1, chart_col_res2 = st.columns([3, 1], gap="small")
        with chart_col_res1:
            st.markdown(f"""
            <div class="subobjective-box quality">
                <div class="subobjective-info">
                    <div class="subobjective-value">{round_value(resilience, 'index'):.1f}/10</div>
                    <div class="subobjective-trend"><span class="trend-up">{res_trend}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_res2:
            if len(resilience_data) > 1:
                res_trend_data = resilience_data.groupby('Month').agg({'Resilience_Score': 'mean'}).reset_index().sort_values('Month')
                fig = create_sparkline(res_trend_data, 'Month', 'Resilience_Score', '#0891b2')
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Escalations
        chart_col_esc1, chart_col_esc2 = st.columns([3, 1], gap="small")
        with chart_col_esc1:
            st.markdown(f"""
            <div class="subobjective-box cost">
                <div class="subobjective-info">
                    <div class="subobjective-value">{round_value(escalations, 'whole'):.0f}</div>
                    <div class="subobjective-trend"><span class="trend-down">{esc_trend}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_esc2:
            if len(escalation_data) > 1:
                esc_trend_data = escalation_data.groupby('Month').agg({'Step_Exception_Count': 'sum'}).reset_index().sort_values('Month')
                fig = create_sparkline(esc_trend_data, 'Month', 'Step_Exception_Count', '#ef4444')
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # -------- OBJECTIVE 3: WORKFORCE & PRODUCTIVITY --------
    with col3:
        capacity_data = filter_data(data['Capacity'])
        work_data = filter_data(data['Work_Models'])
        model_data = filter_data(data['Model_Accuracy'])
        
        avg_capacity = capacity_data['Capacity_Utilization_Percentage'].mean() if len(capacity_data) > 0 else 0
        avg_output = work_data['Output_Per_Hour'].mean() if len(work_data) > 0 else 0
        burnout_count = capacity_data[capacity_data['Burnout_Risk_Flag'] == 'Yes'].shape[0]
        model_accuracy = model_data['Forecast_Accuracy_Percentage'].mean() if len(model_data) > 0 else 0
        
        # Calculate MoM changes
        cap_val, cap_change = get_month_over_month_change(capacity_data, 'Capacity_Utilization_Percentage')
        out_val, out_change = get_month_over_month_change(work_data, 'Output_Per_Hour')
        model_val, model_change = get_month_over_month_change(model_data, 'Forecast_Accuracy_Percentage')
        burnout_change_val = None
        
        cap_trend = f"{round_value(cap_change, 'percentage'):+.1f}% vs last month" if cap_change is not None else "No data"
        out_trend = f"{round_value(out_change, 'percentage'):+.1f}% vs last month" if out_change is not None else "No data"
        model_trend = f"{round_value(model_change, 'percentage'):+.1f}% vs last month" if model_change is not None else "No data"
        
        if st.button("Workforce & Productivity", key="btn_workforce", use_container_width=True, help="Output, Capacity, Health, Model Accuracy"):
            st.session_state.current_page = 'workforce_productivity'
            st.rerun()
        
        st.markdown('<div class="objective-card"><div class="objective-signal">Monitor: Output + Capacity + Health</div>', unsafe_allow_html=True)
        
        # Output/FTE
        chart_col_out1, chart_col_out2 = st.columns([3, 1], gap="small")
        with chart_col_out1:
            st.markdown(f"""
            <div class="subobjective-box efficiency">
                <div class="subobjective-info">
                    <div class="subobjective-value">{round_value(avg_output, 'decimal'):.2f}</div>
                    <div class="subobjective-trend"><span class="trend-up">{out_trend}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_out2:
            if len(work_data) > 1:
                out_trend_data = work_data.groupby('Month').agg({'Output_Per_Hour': 'mean'}).reset_index().sort_values('Month')
                fig = create_sparkline(out_trend_data, 'Month', 'Output_Per_Hour', '#059669')
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Capacity Utilization
        chart_col_cap1, chart_col_cap2 = st.columns([3, 1], gap="small")
        with chart_col_cap1:
            st.markdown(f"""
            <div class="subobjective-box efficiency">
                <div class="subobjective-info">
                    <div class="subobjective-value">{round_value(avg_capacity, 'percentage'):.0f}%</div>
                    <div class="subobjective-trend"><span class="trend-down">{cap_trend}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_cap2:
            if len(capacity_data) > 1:
                cap_trend_data = capacity_data.groupby('Month').agg({'Capacity_Utilization_Percentage': 'mean'}).reset_index().sort_values('Month')
                fig = create_sparkline(cap_trend_data, 'Month', 'Capacity_Utilization_Percentage', '#f59e0b')
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # At-Risk Employees
        chart_col_risk1, chart_col_risk2 = st.columns([3, 1], gap="small")
        with chart_col_risk1:
            st.markdown(f"""
            <div class="subobjective-box cost">
                <div class="subobjective-info">
                    <div class="subobjective-value">{round_value(burnout_count, 'whole'):.0f}</div>
                    <div class="subobjective-trend">Burnout risk count</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_risk2:
            if len(capacity_data) > 1:
                burnout_trend_data = capacity_data[capacity_data['Burnout_Risk_Flag'] == 'Yes'].groupby('Month').size().reset_index(name='count')
                burnout_trend_data = burnout_trend_data.rename(columns={'Month': 'Month', 'count': 'Count'})
                if len(burnout_trend_data) > 0:
                    fig = create_sparkline(burnout_trend_data, 'Month', 'Count', '#ef4444')
                    if fig:
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Model Accuracy
        chart_col_model1, chart_col_model2 = st.columns([3, 1], gap="small")
        with chart_col_model1:
            st.markdown(f"""
            <div class="subobjective-box quality">
                <div class="subobjective-info">
                    <div class="subobjective-value">{round_value(model_accuracy, 'percentage'):.0f}%</div>
                    <div class="subobjective-trend"><span class="trend-up">{model_trend}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with chart_col_model2:
            if len(model_data) > 1:
                model_trend_data = model_data.groupby('Month').agg({'Forecast_Accuracy_Percentage': 'mean'}).reset_index().sort_values('Month')
                fig = create_sparkline(model_trend_data, 'Month', 'Forecast_Accuracy_Percentage', '#059669')
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== DETAIL PAGE 1: COST & EFFICIENCY ====================
elif st.session_state.current_page == 'cost_efficiency':
    show_navigation()
    st.markdown("### Cost & Efficiency - Deep Dive")
    st.markdown("---")
    
    rework_data = filter_data(data['Process_Rework'])
    auto_data = filter_data(data['Automation_ROI'])
    digital_data = filter_data(data['Digital_Index'])
    role_data = filter_data(data['Role_vs_Reality'])
    work_data = filter_data(data['Work_Models'])
    
    st.markdown("#### Detailed Metrics with Trends & Analysis")
    
    # ROW 1: Rework Cost Analysis
    st.markdown("**Rework Cost Analysis**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**KPI Card**")
        rework_pct = rework_data['Rework_Cost_Percentage'].mean()
        rework_dollars = rework_data['Rework_Cost_Dollars'].sum()
        st.metric(label="Rework Cost %", value=f"{round_value(rework_pct, 'percentage'):.1f}%", delta="-0.3%")
        st.metric(label="Total Rework $", value=f"${round_value(rework_dollars, 'currency'):,.0f}")
    
    with col2:
        st.markdown("**By Process (Cost & %)**")
        if len(rework_data) > 0:
            process_rework = rework_data.groupby('Process_Name').agg({
                'Rework_Cost_Dollars': 'sum',
                'Rework_Cost_Percentage': 'mean'
            }).sort_values('Rework_Cost_Dollars', ascending=False).head(6)
            
            fig = go.Figure(data=[
                go.Bar(y=process_rework.index, x=process_rework['Rework_Cost_Dollars'],
                       orientation='h', marker_color='#ef4444', name='Cost ($)', text=[f"${x:,.0f}" for x in process_rework['Rework_Cost_Dollars']],
                       textposition='outside')
            ])
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**By Department**")
        if len(rework_data) > 0:
            dept_rework = rework_data.groupby('Department').agg({
                'Rework_Cost_Dollars': 'sum',
                'Rework_Cost_Percentage': 'mean'
            }).sort_values('Rework_Cost_Dollars', ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(y=dept_rework.index, x=dept_rework['Rework_Cost_Dollars'],
                       orientation='h', marker_color='#dc2626', name='Cost ($)', text=[f"${x:,.0f}" for x in dept_rework['Rework_Cost_Dollars']],
                       textposition='outside')
            ])
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ROW 2: Automation ROI Analysis
    st.markdown("**Automation ROI Potential**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**KPI Card**")
        auto_roi = auto_data['ROI_Percentage_6M'].mean()
        auto_savings = auto_data['Time_Savings_Hours'].sum() if 'Time_Savings_Hours' in auto_data.columns else 0
        st.metric(label="Automation ROI", value=f"{round_value(auto_roi, 'whole'):.0f}%", delta="+4.5%")
        st.metric(label="Time Savings", value=f"{round_value(auto_savings, 'hours'):,.1f} hrs", delta="+450 hrs")
    
    with col2:
        st.markdown("**ROI & Savings Trend**")
        if len(auto_data) > 0:
            agg_dict = {'ROI_Percentage_6M': 'mean'}
            if 'Time_Savings_Hours' in auto_data.columns:
                agg_dict['Time_Savings_Hours'] = 'sum'
            
            auto_trend = auto_data.groupby('Month').agg(agg_dict).reset_index().sort_values('Month')
            
            if len(auto_trend) > 1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=auto_trend['Month'], y=auto_trend['ROI_Percentage_6M'],
                    mode='lines+markers', name='ROI %', line=dict(color='#059669', width=3),
                    marker=dict(size=8), yaxis='y1'
                ))
                if 'Time_Savings_Hours' in auto_trend.columns:
                    fig.add_trace(go.Scatter(
                        x=auto_trend['Month'], y=auto_trend['Time_Savings_Hours'],
                        mode='lines+markers', name='Time Savings (hrs)', line=dict(color='#f59e0b', width=3),
                        marker=dict(size=8), yaxis='y2'
                    ))
                    fig.update_layout(
                        title='ROI & Time Savings Trend', height=250, hovermode='x unified',
                        yaxis=dict(title='ROI %', titlefont=dict(color='#059669'), tickfont=dict(color='#059669')),
                        yaxis2=dict(title='Hours', titlefont=dict(color='#f59e0b'), tickfont=dict(color='#f59e0b'), overlaying='y', side='right'),
                        plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=30, b=0)
                    )
                else:
                    fig.update_layout(
                        title='ROI Trend', height=250, hovermode='x unified',
                        plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=30, b=0)
                    )
                st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**ROI by Task**")
        if len(auto_data) > 0:
            if 'Task_Type' in auto_data.columns:
                task_roi = auto_data.groupby('Task_Type').agg({
                    'ROI_Percentage_6M': 'mean'
                }).sort_values('ROI_Percentage_6M', ascending=False).head(6)
            else:
                task_roi = auto_data.groupby('Process_Name').agg({
                    'ROI_Percentage_6M': 'mean'
                }).sort_values('ROI_Percentage_6M', ascending=False).head(6)
            
            fig = go.Figure(data=[
                go.Bar(y=task_roi.index, x=task_roi['ROI_Percentage_6M'],
                       orientation='h', marker_color='#059669', text=[f"{x:.0f}%" for x in task_roi['ROI_Percentage_6M']],
                       textposition='outside')
            ])
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ROW 3: Digital Workplace Index
    st.markdown("**Digital Workplace Friction Index**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**Gauge Chart**")
        friction = digital_data['Friction_Index_Score'].mean()
        fig = create_gauge_chart(friction, 100, 'Friction Index', '#f59e0b', size='small')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Friction by Department & Process**")
        if len(digital_data) > 0:
            if 'Process' in digital_data.columns:
                dept_proc_friction = digital_data.groupby(['Department', 'Process']).agg({
                    'Friction_Index_Score': 'mean'
                }).reset_index().sort_values('Friction_Index_Score', ascending=False).head(8)
                dept_proc_friction['Label'] = dept_proc_friction['Department'] + ' - ' + dept_proc_friction['Process']
                friction_data = dept_proc_friction
            else:
                dept_friction = digital_data.groupby('Department').agg({
                    'Friction_Index_Score': 'mean'
                }).sort_values('Friction_Index_Score', ascending=False)
                friction_data = dept_friction.reset_index()
                friction_data['Label'] = friction_data['Department']
            
            fig = go.Figure(data=[
                go.Bar(y=friction_data['Label'] if 'Label' in friction_data.columns else friction_data['Department'],
                       x=friction_data['Friction_Index_Score'],
                       orientation='h', marker_color='#f59e0b', text=[f"{x:.1f}" for x in friction_data['Friction_Index_Score']],
                       textposition='outside')
            ])
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**Trend Over Time**")
        if len(digital_data) > 0:
            friction_trend = digital_data.groupby('Month').agg({
                'Friction_Index_Score': 'mean'
            }).reset_index().sort_values('Month')
            
            if len(friction_trend) > 1:
                fig = create_trend_chart(friction_trend, 'Month', 'Friction_Index_Score', 'Friction Trend', '#f59e0b')
                st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ROW 4: Work Model & Role Analysis
    st.markdown("**Work Model Effectiveness & Low-Value Work**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**Work Model Output**")
        if len(work_data) > 0:
            model_output = work_data.groupby('Work_Model').agg({
                'Output_Per_Hour': 'mean'
            })
            
            fig = go.Figure(data=[
                go.Bar(x=model_output.index, y=model_output['Output_Per_Hour'],
                       marker_color=['#059669' if x == model_output['Output_Per_Hour'].max() else '#94a3b8' 
                                    for x in model_output['Output_Per_Hour']])
            ])
            fig.update_layout(height=250, showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Low-Value Work %**")
        if len(role_data) > 0:
            low_value_trend = role_data.groupby('Month').agg({
                'Low_Value_Work_Percentage': 'mean'
            }).reset_index().sort_values('Month')
            
            if len(low_value_trend) > 1:
                fig = create_trend_chart(low_value_trend, 'Month', 'Low_Value_Work_Percentage', 'Low-Value Work Trend', '#dc2626')
                st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**Opportunity Cost by Role**")
        if len(role_data) > 0:
            role_cost = role_data.groupby('Role').agg({
                'Opportunity_Cost_Dollars': 'sum'
            }).sort_values('Opportunity_Cost_Dollars', ascending=False).head(6)
            
            fig = go.Figure(data=[
                go.Bar(y=role_cost.index, x=role_cost['Opportunity_Cost_Dollars'],
                       orientation='h', marker_color='#dc2626')
            ])
            fig.update_layout(height=250, showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### Detailed Data & Export")
    
    tabs = st.tabs(["Rework Cost", "Automation ROI", "Digital Index", "Work Models", "Role Analysis"])
    
    with tabs[0]:
        st.dataframe(rework_data.head(100), use_container_width=True, hide_index=True)
        csv = rework_data.to_csv(index=False)
        st.download_button("Download Rework Data (CSV)", data=csv, file_name="rework_data.csv", mime="text/csv", key="dl_rework")
    
    with tabs[1]:
        st.dataframe(auto_data.head(100), use_container_width=True, hide_index=True)
        csv = auto_data.to_csv(index=False)
        st.download_button("Download Automation Data (CSV)", data=csv, file_name="automation_data.csv", mime="text/csv", key="dl_auto")
    
    with tabs[2]:
        st.dataframe(digital_data.head(100), use_container_width=True, hide_index=True)
        csv = digital_data.to_csv(index=False)
        st.download_button("Download Digital Index (CSV)", data=csv, file_name="digital_index.csv", mime="text/csv", key="dl_digital")
    
    with tabs[3]:
        st.dataframe(work_data.head(100), use_container_width=True, hide_index=True)
        csv = work_data.to_csv(index=False)
        st.download_button("Download Work Models (CSV)", data=csv, file_name="work_models.csv", mime="text/csv", key="dl_work")
    
    with tabs[4]:
        st.dataframe(role_data.head(100), use_container_width=True, hide_index=True)
        csv = role_data.to_csv(index=False)
        st.download_button("Download Role Analysis (CSV)", data=csv, file_name="role_analysis.csv", mime="text/csv", key="dl_role")

# ==================== DETAIL PAGE 2: EXECUTION & RESILIENCE ====================
elif st.session_state.current_page == 'execution_resilience':
    show_navigation()
    st.markdown("### Execution & Resilience - Deep Dive")
    st.markdown("---")
    
    ftr_data = filter_data(data['FTR_Rate'])
    adherence_data = filter_data(data['Adherence'])
    resilience_data = filter_data(data['Resilience'])
    escalation_data = filter_data(data['Escalation'])
    
    st.markdown("#### Detailed Metrics with Trends & Analysis")
    
    # ROW 1: FTR Rate
    st.markdown("**First-Time-Right (FTR) Rate**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**KPI Card**")
        ftr_rate = ftr_data['FTR_Rate_Percentage'].mean()
        st.metric(label="FTR Rate", value=f"{round_value(ftr_rate, 'percentage'):.1f}%", delta="+2.1%")
    
    with col2:
        st.markdown("**Trend Over Time**")
        if len(ftr_data) > 0:
            ftr_trend = ftr_data.groupby('Month').agg({
                'FTR_Rate_Percentage': 'mean'
            }).reset_index().sort_values('Month')
            
            if len(ftr_trend) > 1:
                fig = create_trend_chart(ftr_trend, 'Month', 'FTR_Rate_Percentage', 'FTR Rate Trend', '#059669')
                st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**By Department**")
        if len(ftr_data) > 0:
            dept_ftr = ftr_data.groupby('Department').agg({
                'FTR_Rate_Percentage': 'mean'
            }).sort_values('FTR_Rate_Percentage', ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(y=dept_ftr.index, x=dept_ftr['FTR_Rate_Percentage'],
                       orientation='h', marker_color='#059669', text=[f"{x:.1f}%" for x in dept_ftr['FTR_Rate_Percentage']],
                       textposition='outside')
            ])
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ROW 2: Resilience Score
    st.markdown("**Operational Resilience Score**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**Gauge Chart**")
        resilience = resilience_data['Resilience_Score'].mean()
        fig = create_gauge_chart(resilience, 10, 'Resilience Score', '#0891b2', size='small')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Risk by Task & Department**")
        if len(resilience_data) > 0:
            if 'Department' in resilience_data.columns:
                task_dept_risk = resilience_data.groupby(['Critical_Task', 'Department']).agg({
                    'Risk_Percentage': 'mean'
                }).reset_index().sort_values('Risk_Percentage', ascending=False).head(8)
                task_dept_risk['Label'] = task_dept_risk['Critical_Task'] + ' - ' + task_dept_risk['Department']
                risk_data = task_dept_risk
            else:
                task_risk = resilience_data.groupby('Critical_Task').agg({
                    'Risk_Percentage': 'mean'
                }).sort_values('Risk_Percentage', ascending=False).head(6)
                risk_data = task_risk.reset_index()
                risk_data['Label'] = risk_data['Critical_Task']
            
            fig = go.Figure(data=[
                go.Bar(y=risk_data['Label'] if 'Label' in risk_data.columns else risk_data['Critical_Task'],
                       x=risk_data['Risk_Percentage'],
                       orientation='h', marker_color='#ef4444', text=[f"{x:.1f}%" for x in risk_data['Risk_Percentage']],
                       textposition='outside')
            ])
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**Trend Over Time**")
        if len(resilience_data) > 0:
            resilience_trend = resilience_data.groupby('Month').agg({
                'Resilience_Score': 'mean'
            }).reset_index().sort_values('Month')
            
            if len(resilience_trend) > 1:
                fig = create_trend_chart(resilience_trend, 'Month', 'Resilience_Score', 'Resilience Trend', '#0891b2')
                st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ROW 3: Process Adherence
    st.markdown("**Process Adherence Rate**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**KPI Card**")
        adherence = adherence_data['Adherence_Rate_Percentage'].mean()
        st.metric(label="Adherence Rate", value=f"{round_value(adherence, 'percentage'):.1f}%", delta="-1.2%")
    
    with col2:
        st.markdown("**By Department**")
        if len(adherence_data) > 0:
            dept_adherence = adherence_data.groupby('Department').agg({
                'Adherence_Rate_Percentage': 'mean'
            }).sort_values('Adherence_Rate_Percentage', ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(y=dept_adherence.index, x=dept_adherence['Adherence_Rate_Percentage'],
                       orientation='h', marker_color='#1e40af', text=[f"{x:.1f}%" for x in dept_adherence['Adherence_Rate_Percentage']],
                       textposition='outside')
            ])
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**By Process Step**")
        if len(adherence_data) > 0:
            if 'Process_Step' in adherence_data.columns:
                step_adherence = adherence_data.groupby('Process_Step').agg({
                    'Adherence_Rate_Percentage': 'mean'
                }).sort_values('Adherence_Rate_Percentage', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(y=step_adherence.index, x=step_adherence['Adherence_Rate_Percentage'],
                           orientation='h', marker_color='#0891b2', text=[f"{x:.1f}%" for x in step_adherence['Adherence_Rate_Percentage']],
                           textposition='outside')
                ])
                fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
                st.plotly_chart(fig, use_container_width=True)
            else:
                adherence_trend = adherence_data.groupby('Month').agg({
                    'Adherence_Rate_Percentage': 'mean'
                }).reset_index().sort_values('Month')
                
                if len(adherence_trend) > 1:
                    fig = create_trend_chart(adherence_trend, 'Month', 'Adherence_Rate_Percentage', 'Adherence Trend', '#0891b2')
                    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ROW 4: Escalations
    st.markdown("**Escalation & Exception Patterns**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**Total Escalations**")
        escalations = escalation_data['Step_Exception_Count'].sum()
        st.metric(label="Escalations", value=f"{round_value(escalations, 'whole'):.0f}", delta="+8%")
    
    with col2:
        st.markdown("**By Process**")
        if len(escalation_data) > 0:
            process_esc = escalation_data.groupby('Process').agg({
                'Step_Exception_Count': 'sum'
            }).sort_values('Step_Exception_Count', ascending=False).head(6)
            
            fig = go.Figure(data=[
                go.Bar(y=process_esc.index, x=process_esc['Step_Exception_Count'],
                       orientation='h', marker_color='#ef4444', text=[f"{int(x)}" for x in process_esc['Step_Exception_Count']],
                       textposition='outside')
            ])
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**By Department**")
        if len(escalation_data) > 0:
            dept_esc = escalation_data.groupby('Department').agg({
                'Step_Exception_Count': 'sum'
            }).sort_values('Step_Exception_Count', ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(y=dept_esc.index, x=dept_esc['Step_Exception_Count'],
                       orientation='h', marker_color='#dc2626', text=[f"{int(x)}" for x in dept_esc['Step_Exception_Count']],
                       textposition='outside')
            ])
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### Detailed Data & Export")
    
    tabs = st.tabs(["FTR Rate", "Adherence", "Resilience", "Escalations"])
    
    with tabs[0]:
        st.dataframe(ftr_data.head(100), use_container_width=True, hide_index=True)
        csv = ftr_data.to_csv(index=False)
        st.download_button("Download FTR Data (CSV)", data=csv, file_name="ftr_data.csv", mime="text/csv", key="dl_ftr")
    
    with tabs[1]:
        st.dataframe(adherence_data.head(100), use_container_width=True, hide_index=True)
        csv = adherence_data.to_csv(index=False)
        st.download_button("Download Adherence Data (CSV)", data=csv, file_name="adherence_data.csv", mime="text/csv", key="dl_adherence")
    
    with tabs[2]:
        st.dataframe(resilience_data.head(100), use_container_width=True, hide_index=True)
        csv = resilience_data.to_csv(index=False)
        st.download_button("Download Resilience Data (CSV)", data=csv, file_name="resilience_data.csv", mime="text/csv", key="dl_resilience")
    
    with tabs[3]:
        st.dataframe(escalation_data.head(100), use_container_width=True, hide_index=True)
        csv = escalation_data.to_csv(index=False)
        st.download_button("Download Escalation Data (CSV)", data=csv, file_name="escalation_data.csv", mime="text/csv", key="dl_escalation")

# ==================== DETAIL PAGE 3: WORKFORCE & PRODUCTIVITY ====================
elif st.session_state.current_page == 'workforce_productivity':
    show_navigation()
    st.markdown("### Workforce & Productivity - Deep Dive")
    st.markdown("---")
    
    capacity_data = filter_data(data['Capacity'])
    work_data = filter_data(data['Work_Models'])
    model_data = filter_data(data['Model_Accuracy'])
    collab_data = filter_data(data['Collaboration'])
    
    st.markdown("#### Detailed Metrics with Trends & Analysis")
    
    # ROW 1: Output & Productivity
    st.markdown("**Output & Productivity per FTE**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**KPI Card**")
        avg_output = work_data['Output_Per_Hour'].mean()
        st.metric(label="Output/FTE", value=f"{round_value(avg_output, 'decimal'):.3f}", delta="+0.3")
    
    with col2:
        st.markdown("**By Department**")
        if len(work_data) > 0:
            dept_output = work_data.groupby('Department').agg({
                'Output_Per_Hour': 'mean'
            }).sort_values('Output_Per_Hour', ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(y=dept_output.index, x=dept_output['Output_Per_Hour'],
                       orientation='h', marker_color='#059669', text=[f"{x:.3f}" for x in dept_output['Output_Per_Hour']],
                       textposition='outside')
            ])
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**Trend Over Time**")
        if len(work_data) > 0:
            output_trend = work_data.groupby('Month').agg({
                'Output_Per_Hour': 'mean'
            }).reset_index().sort_values('Month')
            
            if len(output_trend) > 1:
                fig = create_trend_chart(output_trend, 'Month', 'Output_Per_Hour', 'Output Trend', '#059669')
                st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ROW 2: Capacity Utilization
    st.markdown("**Capacity Utilization & Workload**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**Dial Chart**")
        avg_capacity = capacity_data['Capacity_Utilization_Percentage'].mean()
        fig = create_gauge_chart(avg_capacity, 150, 'Capacity %', '#f59e0b', size='small')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**By Department (Utilization)**")
        if len(capacity_data) > 0:
            dept_capacity = capacity_data.groupby('Department').agg({
                'Capacity_Utilization_Percentage': 'mean'
            }).sort_values('Capacity_Utilization_Percentage', ascending=False)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=dept_capacity.index, x=dept_capacity['Capacity_Utilization_Percentage'],
                orientation='h', marker_color='#f59e0b', name='Capacity %',
                text=[f"{x:.0f}%" for x in dept_capacity['Capacity_Utilization_Percentage']],
                textposition='outside'
            ))
            fig.add_vline(x=100, line_dash="dash", line_color="red", annotation_text="Target", annotation_position="top right")
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified', xaxis_title='Utilization %')
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**Trend Over Time**")
        if len(capacity_data) > 0:
            capacity_trend = capacity_data.groupby('Month').agg({
                'Capacity_Utilization_Percentage': 'mean'
            }).reset_index().sort_values('Month')
            
            if len(capacity_trend) > 1:
                fig = create_trend_chart(capacity_trend, 'Month', 'Capacity_Utilization_Percentage', 'Capacity Trend', '#f59e0b')
                st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ROW 3: Model Accuracy
    st.markdown("**Capacity Model Accuracy**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**KPI Card**")
        model_accuracy = model_data['Forecast_Accuracy_Percentage'].mean()
        st.metric(label="Model Accuracy", value=f"{round_value(model_accuracy, 'percentage'):.1f}%", delta="+3.2%")
    
    with col2:
        st.markdown("**By Department**")
        if len(model_data) > 0:
            dept_model = model_data.groupby('Department').agg({
                'Forecast_Accuracy_Percentage': 'mean'
            }).sort_values('Forecast_Accuracy_Percentage', ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(y=dept_model.index, x=dept_model['Forecast_Accuracy_Percentage'],
                       orientation='h', marker_color='#1e40af', text=[f"{x:.1f}%" for x in dept_model['Forecast_Accuracy_Percentage']],
                       textposition='outside')
            ])
            fig.update_layout(height=280, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified')
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**Staffing Variance**")
        if len(model_data) > 0:
            if 'Staffing_Variance_Percentage' in model_data.columns:
                variance_data = model_data.groupby('Month').agg({
                    'Staffing_Variance_Percentage': 'mean'
                }).reset_index().sort_values('Month')
                
                if len(variance_data) > 1:
                    fig = create_trend_chart(variance_data, 'Month', 'Staffing_Variance_Percentage', 'Staffing Variance Trend', '#dc2626')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                model_trend = model_data.groupby('Month').agg({
                    'Forecast_Accuracy_Percentage': 'mean'
                }).reset_index().sort_values('Month')
                
                if len(model_trend) > 1:
                    fig = create_trend_chart(model_trend, 'Month', 'Forecast_Accuracy_Percentage', 'Model Accuracy Trend', '#1e40af')
                    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ROW 4: Employee Health
    st.markdown("**Employee Health & At-Risk Employees**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**Health Summary**")
        burnout_count = capacity_data[capacity_data['Burnout_Risk_Flag'] == 'Yes'].shape[0]
        total_employees = len(capacity_data)
        burnout_pct = (burnout_count / total_employees * 100) if total_employees > 0 else 0
        st.metric(label="At-Risk Employees", value=f"{round_value(burnout_count, 'whole'):.0f}", delta="+2")
        st.metric(label="At-Risk %", value=f"{round_value(burnout_pct, 'percentage'):.1f}%")
    
    with col2:
        st.markdown("**At-Risk & Capacity by Dept**")
        if len(capacity_data) > 0:
            at_risk_capacity = capacity_data.groupby('Department').agg({
                'Burnout_Risk_Flag': lambda x: (x == 'Yes').sum(),
                'Capacity_Utilization_Percentage': 'mean'
            }).reset_index()
            at_risk_capacity.columns = ['Department', 'At_Risk_Count', 'Avg_Capacity']
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=at_risk_capacity['Department'], x=at_risk_capacity['At_Risk_Count'],
                orientation='h', name='At-Risk', marker_color='#ef4444', text=[f"{int(x)}" for x in at_risk_capacity['At_Risk_Count']],
                textposition='outside'
            ))
            fig.add_trace(go.Scatter(
                y=at_risk_capacity['Department'], x=at_risk_capacity['Avg_Capacity'],
                mode='lines+markers', name='Avg Capacity %', line=dict(color='#f59e0b', width=3),
                marker=dict(size=8), yaxis='y', xaxis='x2'
            ))
            fig.update_layout(
                height=280, plot_bgcolor="rgba(0,0,0,0)", hovermode='y unified',
                xaxis=dict(title='At-Risk Count'), xaxis2=dict(title='Capacity %', overlaying='x', side='top')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**Collaboration Trend**")
        if len(collab_data) > 0:
            collab_trend = collab_data.groupby('Month').agg({
                'Collaboration_Tools_Time_Hours': 'mean'
            }).reset_index().sort_values('Month')
            
            if len(collab_trend) > 1:
                fig = create_trend_chart(collab_trend, 'Month', 'Collaboration_Tools_Time_Hours', 'Collaboration Hours Trend', '#0891b2')
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### Detailed Data & Export")
    
    tabs = st.tabs(["Capacity", "Work Models", "Model Accuracy", "Collaboration"])
    
    with tabs[0]:
        st.dataframe(capacity_data.head(100), use_container_width=True, hide_index=True)
        csv = capacity_data.to_csv(index=False)
        st.download_button("Download Capacity Data (CSV)", data=csv, file_name="capacity_data.csv", mime="text/csv", key="dl_capacity")
    
    with tabs[1]:
        st.dataframe(work_data.head(100), use_container_width=True, hide_index=True)
        csv = work_data.to_csv(index=False)
        st.download_button("Download Work Models (CSV)", data=csv, file_name="work_models_data.csv", mime="text/csv", key="dl_workmodels")
    
    with tabs[2]:
        st.dataframe(model_data.head(100), use_container_width=True, hide_index=True)
        csv = model_data.to_csv(index=False)
        st.download_button("Download Model Accuracy (CSV)", data=csv, file_name="model_accuracy.csv", mime="text/csv", key="dl_model")
    
    with tabs[3]:
        st.dataframe(collab_data.head(100), use_container_width=True, hide_index=True)
        csv = collab_data.to_csv(index=False)
        st.download_button("Download Collaboration (CSV)", data=csv, file_name="collaboration_data.csv", mime="text/csv", key="dl_collab")

# ==================== FOOTER ====================
st.divider()
st.markdown(f"""
    <div style="text-align: center; padding: 15px; color: #6b7280; font-size: 11px;">
        <strong>COO Dashboard v12.0 - Professional Edition</strong> | 
        {len(selected_months)} months | {len(dept_filter) if dept_filter else len(all_departments)} departments | 
        Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
""", unsafe_allow_html=True)
