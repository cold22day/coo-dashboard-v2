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

# ==================== CUSTOM CSS WITH IMPROVEMENTS ====================
st.markdown("""
    <style>
    .main { padding: 0px; }

    /* IMPROVED: Objective Card with better vertical centering */
    .objective-card {
        background: white;
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
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
    
    /* Streamlit button styling */
    .stButton > button {
        width: 100%;
        padding: 14px;
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        font-size: 13px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #1e40af;
        margin: 8px 0;
    }
    
    .metric-trend {
        font-size: 12px;
        font-weight: 600;
    }
    
    .trend-up { color: #059669; }
    .trend-down { color: #ef4444; }
    .trend-neutral { color: #6b7280; }
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE FOR NAVIGATION ====================
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home'

def navigate_to(view):
    """Navigate to a different view"""
    st.session_state.current_view = view
    st.rerun()

# ==================== MOCK DATA GENERATOR ====================
@st.cache_data
def create_mock_role_reality_data():
    """Creates realistic mock data for Role vs. Reality Analysis"""
    np.random.seed(42)
    
    roles = ['Senior Engineer', 'Sales Manager', 'Data Analyst', 'Product Manager', 
             'Marketing Lead', 'Finance Analyst', 'Operations Manager', 'HR Business Partner']
    departments = ['Engineering', 'Sales', 'Analytics', 'Product', 
                   'Marketing', 'Finance', 'Operations', 'HR']
    months = pd.date_range('2025-04-01', '2025-09-01', freq='MS')
    
    data_list = []
    
    for month in months:
        for i, (role, dept) in enumerate(zip(roles, departments)):
            for emp_num in range(np.random.randint(3, 6)):
                emp_id = f"{dept[:3].upper()}{i:02d}{emp_num}"
                
                salary_map = {
                    'Senior Engineer': np.random.randint(110000, 140000),
                    'Sales Manager': np.random.randint(90000, 120000),
                    'Data Analyst': np.random.randint(70000, 90000),
                    'Product Manager': np.random.randint(100000, 130000),
                    'Marketing Lead': np.random.randint(80000, 110000),
                    'Finance Analyst': np.random.randint(65000, 85000),
                    'Operations Manager': np.random.randint(75000, 95000),
                    'HR Business Partner': np.random.randint(70000, 90000)
                }
                
                annual_salary = salary_map[role]
                total_hours = 160
                
                if role == 'Senior Engineer':
                    core_pct = np.random.uniform(0.50, 0.70)
                    repetitive_pct = np.random.uniform(0.15, 0.30)
                    admin_pct = np.random.uniform(0.05, 0.15)
                elif role in ['Sales Manager', 'Product Manager']:
                    core_pct = np.random.uniform(0.40, 0.60)
                    repetitive_pct = np.random.uniform(0.10, 0.25)
                    admin_pct = np.random.uniform(0.10, 0.25)
                else:
                    core_pct = np.random.uniform(0.45, 0.65)
                    repetitive_pct = np.random.uniform(0.10, 0.25)
                    admin_pct = np.random.uniform(0.08, 0.20)
                
                collaboration_pct = 1 - (core_pct + repetitive_pct + admin_pct)
                
                core_hours = total_hours * core_pct
                repetitive_hours = total_hours * repetitive_pct
                admin_hours = total_hours * admin_pct
                collaboration_hours = total_hours * collaboration_pct
                
                hourly_rate = annual_salary / 2080
                low_value_hours = repetitive_hours + admin_hours
                opportunity_cost = low_value_hours * hourly_rate
                
                data_list.append({
                    'Employee_ID': emp_id,
                    'Role': role,
                    'Department': dept,
                    'Month': month,
                    'Annual_Salary': annual_salary,
                    'Hourly_Rate': hourly_rate,
                    'Total_Hours': total_hours,
                    'Core_Hours': core_hours,
                    'Admin_Hours': admin_hours,
                    'Repetitive_Hours': repetitive_hours,
                    'Collaboration_Hours': collaboration_hours,
                    'Low_Value_Hours': low_value_hours,
                    'Low_Value_Percentage': (low_value_hours / total_hours) * 100,
                    'Opportunity_Cost_Monthly': opportunity_cost
                })
    
    return pd.DataFrame(data_list)

@st.cache_data
def create_mock_process_data():
    """Create mock data for process metrics"""
    np.random.seed(42)
    
    processes = ['HR Onboarding', 'Customer Onboarding', 'Procurement', 
                 'Claims Processing', 'Invoice-to-Payment']
    departments = ['HR', 'Sales', 'Finance', 'Operations', 'Finance']
    
    data_list = []
    for process, dept in zip(processes, departments):
        data_list.append({
            'Process': process,
            'Department': dept,
            'Rework_Cost': np.random.randint(15000, 35000),
            'Rework_Percentage': np.random.uniform(3.5, 6.5)
        })
    
    return pd.DataFrame(data_list)

@st.cache_data
def create_mock_department_data():
    """Create mock data for department metrics"""
    np.random.seed(43)
    
    departments = ['Finance', 'HR', 'Sales', 'Engineering', 'Operations', 'Marketing']
    
    data_list = []
    for dept in departments:
        data_list.append({
            'Department': dept,
            'Rework_Cost': np.random.randint(2000, 35000),
            'Avg_Efficiency': np.random.uniform(75, 95)
        })
    
    return pd.DataFrame(data_list)

# ==================== HELPER FUNCTIONS ====================
def create_improved_sparkline(values, trend_type='neutral'):
    """IMPROVED: Create sparkline with trend-based colors and labels"""
    
    # Determine color based on trend
    if trend_type == 'up':
        color = '#059669'  # Green for positive
        fill_color = 'rgba(5, 150, 105, 0.2)'
    elif trend_type == 'down':
        color = '#ef4444'  # Red for negative
        fill_color = 'rgba(239, 68, 68, 0.2)'
    else:
        color = '#6b7280'  # Gray for neutral
        fill_color = 'rgba(107, 114, 128, 0.2)'
    
    fig = go.Figure()
    
    # Add area trace
    fig.add_trace(go.Scatter(
        y=values,
        mode='lines',
        line=dict(color=color, width=2.5),
        fill='tozeroy',
        fillcolor=fill_color,
        showlegend=False,
        hovertemplate='Value: %{y:.1f}<extra></extra>'
    ))
    
    # Add markers at start and end
    fig.add_trace(go.Scatter(
        x=[0, len(values)-1],
        y=[values[0], values[-1]],
        mode='markers',
        marker=dict(size=6, color=color, line=dict(width=2, color='white')),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        height=60,
        width=120,
        margin=dict(l=0, r=0, t=5, b=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='closest'
    )
    
    return fig

def create_dynamic_horizontal_bar(df, x_col, y_col, title, color_scale='Reds'):
    """IMPROVED: Create dynamic horizontal bar chart with gradient colors"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df[y_col],
        x=df[x_col],
        orientation='h',
        marker=dict(
            color=df[x_col],
            colorscale=color_scale,
            showscale=False,
            line=dict(width=0)
        ),
        text=[f"${x:,.0f}" for x in df[x_col]],
        textposition='outside',
        textfont=dict(size=12, weight='bold', color='#1f2937'),
        hovertemplate='<b>%{y}</b><br>Cost: $%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=16, weight='bold', color='#1f2937')),
        xaxis_title='',
        yaxis_title='',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=20, r=60, t=60, b=40),
        yaxis=dict(autorange='reversed')
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False)
    fig.update_yaxes(showgrid=False)
    
    return fig

def create_stacked_bar_improved(df, categories, values_dict, title):
    """IMPROVED: Create stacked bar chart with better colors and labels"""
    fig = go.Figure()
    
    colors = {
        'Core Work': '#27ae60',
        'Collaboration': '#3498db',
        'Admin': '#f39c12',
        'Repetitive': '#e74c3c'
    }
    
    for name, values in values_dict.items():
        fig.add_trace(go.Bar(
            name=name,
            x=categories,
            y=values,
            marker_color=colors.get(name, '#1e40af'),
            text=[f"{v:.0f}h" for v in values],
            textposition='inside',
            textfont=dict(color='white', size=11, weight='bold'),
            hovertemplate=f'<b>{name}</b><br>%{{x}}<br>Hours: %{{y:.1f}}<extra></extra>'
        ))
    
    fig.update_layout(
        barmode='stack',
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=16, weight='bold', color='#1f2937')),
        xaxis_title='',
        yaxis_title='Hours per Month',
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#e5e7eb',
            borderwidth=1
        ),
        margin=dict(l=50, r=20, t=80, b=100)
    )
    
    fig.update_xaxes(tickangle=-45, showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    
    return fig

def create_gradient_horizontal_bar(df, x_col, y_col, title):
    """IMPROVED: Create horizontal bar with beautiful gradient"""
    fig = go.Figure()
    
    df_sorted = df.sort_values(x_col, ascending=True)
    
    fig.add_trace(go.Bar(
        y=df_sorted[y_col],
        x=df_sorted[x_col],
        orientation='h',
        marker=dict(
            color=df_sorted[x_col],
            colorscale=[[0, '#3b82f6'], [0.5, '#8b5cf6'], [1, '#ec4899']],
            showscale=False,
            line=dict(width=0)
        ),
        text=[f"${x:,.0f}" for x in df_sorted[x_col]],
        textposition='outside',
        textfont=dict(size=12, weight='bold', color='#1f2937'),
        hovertemplate='<b>%{y}</b><br>Cost: $%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=16, weight='bold', color='#1f2937')),
        xaxis_title='Monthly Opportunity Cost ($)',
        yaxis_title='',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(l=20, r=60, t=60, b=60)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(showgrid=False)
    
    return fig

def create_trend_line_dual_axis(df, x_col, y1_col, y2_col, title):
    """Create trend line with dual Y-axis"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y1_col],
        mode='lines+markers',
        name='Low-Value %',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10, line=dict(width=2, color='white')),
        yaxis='y1',
        hovertemplate='%{x}<br>Low-Value: %{y:.1f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y2_col],
        name='Monthly Cost',
        marker_color='#95a5a6',
        opacity=0.5,
        yaxis='y2',
        hovertemplate='%{x}<br>Cost: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=16, weight='bold')),
        yaxis=dict(
            title=dict(text="Low-Value Work %", font=dict(color='#e74c3c', size=12, weight='bold')),
            tickfont=dict(color='#e74c3c')
        ),
        yaxis2=dict(
            title=dict(text="Opportunity Cost ($)", font=dict(color='#95a5a6', size=12, weight='bold')),
            tickfont=dict(color='#95a5a6'),
            overlaying='y',
            side='right'
        ),
        xaxis_title="Month",
        showlegend=True,
        legend=dict(x=0.5, xanchor='center', y=-0.2, orientation='h'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        height=400,
        margin=dict(l=60, r=60, t=60, b=80)
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    
    return fig

# ==================== LOAD DATA ====================
@st.cache_data
def load_excel_data():
    """Load data from Excel file or use mock data"""
    try:
        excel_file = 'COO_ROI_Dashboard_KPIs_Complete_12.xlsx'
        data = {
            'Role_vs_Reality': pd.read_excel(excel_file, sheet_name='Role_vs_Reality_Analysis'),
            'Process_Rework': pd.read_excel(excel_file, sheet_name='Process_Rework_Cost'),
        }
        return data
    except FileNotFoundError:
        st.warning("📁 Excel file not found. Using mock data for demonstration.")
        return {
            'Role_vs_Reality': create_mock_role_reality_data(),
            'Process_Rework': create_mock_process_data(),
        }

data = load_excel_data()

# ==================== MAIN APP ====================

# HEADER
st.title("🎯 COO Performance Dashboard")
st.markdown("**Unified view of Cost, Execution, and Workforce metrics**")
st.markdown("---")

# ==================== HOME VIEW ====================
if st.session_state.current_view == 'home':
    st.markdown("## Key Objectives")
    
    # Create three columns for the main objective cards
    cols = st.columns(3)
    
    objectives = [
        {
            'title': 'Cost & Efficiency',
            'signal': 'Monitor: ROI + Rework + Automation Coverage',
            'key': 'cost',
            'metrics': [
                {'name': 'Rework Cost %', 'value': '4.3%', 'trend': '+6.7% vs last month', 'trend_type': 'down', 'sparkline': [4.5, 4.2, 4.8, 4.3, 4.1, 4.3]},
                {'name': 'Automation ROI', 'value': '979%', 'trend': '+101.1% vs last month', 'trend_type': 'up', 'sparkline': [850, 880, 920, 950, 970, 979]},
                {'name': 'Automation Coverage', 'value': '100%', 'trend': 'Process automation', 'trend_type': 'neutral', 'sparkline': [95, 96, 97, 98, 99, 100]},
                {'name': 'Digital Index', 'value': '65.7', 'trend': '+31.4% vs last month', 'trend_type': 'up', 'sparkline': [50, 52, 58, 60, 63, 65.7]},
            ]
        },
        {
            'title': 'Execution & Resilience',
            'signal': 'Monitor: Quality + Reliability + Risk',
            'key': 'execution',
            'metrics': [
                {'name': 'FTR Rate', 'value': '75.3%', 'trend': '-10.2% vs last month', 'trend_type': 'down', 'sparkline': [80, 78, 76, 75, 74, 75.3]},
                {'name': 'Process Adherence', 'value': '80.1%', 'trend': '-17.2% vs last month', 'trend_type': 'down', 'sparkline': [90, 88, 85, 82, 80, 80.1]},
                {'name': 'Resilience Score', 'value': '6.1/10', 'trend': '+0.0% vs last month', 'trend_type': 'neutral', 'sparkline': [6.0, 6.1, 6.0, 6.1, 6.1, 6.1]},
                {'name': 'Escalations', 'value': '1907', 'trend': '-67.6% vs last month', 'trend_type': 'up', 'sparkline': [2500, 2300, 2100, 2000, 1950, 1907]},
            ]
        },
        {
            'title': 'Workforce & Productivity',
            'signal': 'Monitor: Output + Capacity + Health',
            'key': 'workforce',
            'metrics': [
                {'name': 'Output Index', 'value': '8.00', 'trend': '-5.5% vs last month', 'trend_type': 'down', 'sparkline': [8.5, 8.4, 8.3, 8.2, 8.1, 8.0]},
                {'name': 'Capacity Utilization', 'value': '95%', 'trend': '+4.3% vs last month', 'trend_type': 'up', 'sparkline': [90, 91, 92, 93, 94, 95]},
                {'name': 'Burnout Risk', 'value': '24', 'trend': 'Burnout risk count', 'trend_type': 'down', 'sparkline': [30, 28, 26, 25, 24, 24]},
                {'name': 'Model Accuracy', 'value': '85%', 'trend': '+5.5% vs last month', 'trend_type': 'up', 'sparkline': [80, 81, 82, 83, 84, 85]},
            ]
        }
    ]
    
    for idx, obj in enumerate(objectives):
        with cols[idx]:
            st.markdown(f"""
                <div class="objective-card">
                    <div class="objective-header">{obj['title']}</div>
                    <div class="objective-signal">{obj['signal']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Display metrics with clickable cards - ALL GO TO SAME DASHBOARD
            for metric in obj['metrics']:
                trend_class = f"trend-{metric['trend_type']}"
                
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    # ALL BUTTONS FOR SAME OBJECTIVE GO TO SAME DASHBOARD
                    if st.button(f"📊 {metric['name']}", key=f"btn_{obj['key']}_{metric['name']}", use_container_width=True):
                        navigate_to(obj['key'])  # All cards navigate to the same view
                    
                    st.markdown(f"""
                        <div class="metric-value">{metric['value']}</div>
                        <div class="metric-trend {trend_class}">{metric['trend']}</div>
                    """, unsafe_allow_html=True)
                
                with col_b:
                    # IMPROVED: Sparkline with trend-based colors
                    sparkline_fig = create_improved_sparkline(
                        metric['sparkline'],
                        trend_type=metric['trend_type']
                    )
                    st.plotly_chart(sparkline_fig, use_container_width=True, config={'displayModeBar': False})
                
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ==================== COST & EFFICIENCY VIEW ====================
elif st.session_state.current_view == 'cost':
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            navigate_to('home')
    with col2:
        st.markdown("## 💰 Cost & Efficiency Dashboard")
    
    st.markdown("### 📊 Role vs. Reality Analysis")
    
    try:
        role_reality_data = data['Role_vs_Reality']
        
        if role_reality_data.empty:
            st.error("No data available")
        else:
            latest_month = role_reality_data['Month'].max()
            current_data = role_reality_data[role_reality_data['Month'] == latest_month]
            
            # KPI Cards with error handling
            col1, col2, col3, col4 = st.columns(4)
            
            # Safe calculation with error handling
            if 'Opportunity_Cost_Monthly' in current_data.columns:
                total_opportunity_cost = current_data['Opportunity_Cost_Monthly'].sum()
                annualized_cost = total_opportunity_cost * 12
            else:
                total_opportunity_cost = 0
                annualized_cost = 0
            
            if 'Low_Value_Percentage' in current_data.columns:
                avg_low_value_pct = current_data['Low_Value_Percentage'].mean()
                high_risk_roles = len(current_data[current_data['Low_Value_Percentage'] > 30])
            else:
                avg_low_value_pct = 0
                high_risk_roles = 0
            
            with col1:
                st.metric("Monthly Opportunity Cost", f"${total_opportunity_cost:,.0f}", delta="-12%", delta_color="inverse")
            with col2:
                st.metric("Avg Low-Value Work", f"{avg_low_value_pct:.1f}%", delta="-5%", delta_color="inverse")
            with col3:
                st.metric("High-Risk Roles (>30%)", f"{high_risk_roles}", delta="-2", delta_color="inverse")
            with col4:
                st.metric("Annualized Impact", f"${annualized_cost:,.0f}")
            
            st.markdown("---")
            
            # Charts with error handling
            col1, col2 = st.columns(2)
            
            with col1:
                try:
                    required_cols = ['Role', 'Core_Hours', 'Admin_Hours', 'Repetitive_Hours', 'Collaboration_Hours']
                    if all(col in current_data.columns for col in required_cols):
                        role_breakdown = current_data.groupby('Role').agg({
                            'Core_Hours': 'mean',
                            'Admin_Hours': 'mean',
                            'Repetitive_Hours': 'mean',
                            'Collaboration_Hours': 'mean'
                        }).round(1).reset_index()
                        
                        fig = create_stacked_bar_improved(
                            role_breakdown,
                            role_breakdown['Role'].tolist(),
                            {
                                'Core Work': role_breakdown['Core_Hours'].tolist(),
                                'Collaboration': role_breakdown['Collaboration_Hours'].tolist(),
                                'Admin': role_breakdown['Admin_Hours'].tolist(),
                                'Repetitive': role_breakdown['Repetitive_Hours'].tolist()
                            },
                            "Time Allocation by Role"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Required columns missing for Time Allocation chart")
                except Exception as e:
                    st.error(f"Error creating Time Allocation chart: {str(e)}")
            
            with col2:
                try:
                    if 'Role' in current_data.columns and 'Opportunity_Cost_Monthly' in current_data.columns:
                        role_cost = current_data.groupby('Role').agg({
                            'Opportunity_Cost_Monthly': 'sum'
                        }).sort_values('Opportunity_Cost_Monthly', ascending=True).reset_index()
                        
                        fig = create_gradient_horizontal_bar(
                            role_cost,
                            'Opportunity_Cost_Monthly',
                            'Role',
                            "Opportunity Cost by Role"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Required columns missing for Opportunity Cost chart")
                except Exception as e:
                    st.error(f"Error creating Opportunity Cost chart: {str(e)}")
            
            # Trend Over Time
            st.markdown("### 📈 Trend Over Time")
            
            try:
                if 'Month' in role_reality_data.columns and 'Low_Value_Percentage' in role_reality_data.columns and 'Opportunity_Cost_Monthly' in role_reality_data.columns:
                    monthly_trend = role_reality_data.groupby('Month').agg({
                        'Low_Value_Percentage': 'mean',
                        'Opportunity_Cost_Monthly': 'sum'
                    }).reset_index()
                    
                    monthly_trend['Month_Str'] = monthly_trend['Month'].dt.strftime('%Y-%m')
                    
                    fig = create_trend_line_dual_axis(
                        monthly_trend,
                        'Month_Str',
                        'Low_Value_Percentage',
                        'Opportunity_Cost_Monthly',
                        'Low-Value Work Trend Over Time'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Required columns missing for Trend chart")
            except Exception as e:
                st.error(f"Error creating Trend chart: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading Cost & Efficiency dashboard: {str(e)}")
        st.info("Please check that your data file has the required columns.")

# ==================== EXECUTION & RESILIENCE VIEW ====================
elif st.session_state.current_view == 'execution':
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            navigate_to('home')
    with col2:
        st.markdown("## ✅ Execution & Resilience Dashboard")
    
    st.info("📊 Coming soon: Process quality, reliability, and risk metrics")

# ==================== WORKFORCE & PRODUCTIVITY VIEW ====================
elif st.session_state.current_view == 'workforce':
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            navigate_to('home')
    with col2:
        st.markdown("## 👥 Workforce & Productivity Dashboard")
    
    st.info("📊 Coming soon: Output, capacity, and health metrics")

# ==================== FOOTER ====================
st.divider()
st.markdown(f"""
    <div style="text-align: center; padding: 15px; color: #6b7280; font-size: 11px;">
        <strong>COO Dashboard - Enhanced Version v2.1</strong> | 
        Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
""", unsafe_allow_html=True)