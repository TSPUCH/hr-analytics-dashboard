import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# --- Page Configuration ---
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Sidebar Gradient ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-image: linear-gradient(to bottom, #4F008C, #000);
    }
</style>
""", unsafe_allow_html=True)

# --- Database Connection ---
DB_PATH = 'hr_database.db'

def get_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def run_query(query, params=None):
    """Runs a SQL query and returns the result as a DataFrame."""
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

def execute_query(query, params=None):
    """Executes a non-select SQL query (INSERT, UPDATE)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        conn.commit()

# --- Load Initial Data ---
try:
    df = run_query("SELECT * FROM employees")
except Exception as e:
    st.error(f"Failed to load data from the database: {e}")
    st.info("Please ensure you have run 'python setup_database.py' to create the database.")
    st.stop()

# --- Sidebar ---
st.sidebar.image("https://placehold.co/200x100/FF375E/FFFFFF?text=Company+Logo", use_container_width=True)
st.sidebar.header("Dashboard Filters & Actions")

# 1. Department Filter
department = st.sidebar.selectbox(
    "Select a Department:",
    options=['All'] + sorted(df['Department'].unique().tolist())
)

# Filter data based on selection
if department != 'All':
    df_filtered = df[df['Department'] == department]
else:
    df_filtered = df.copy()

# 2. Add New Employee Form
with st.sidebar.form("new_employee_form", clear_on_submit=True):
    st.subheader("Add New Employee")
    new_id = st.number_input("Employee ID", min_value=df['EmployeeID'].max() + 1, step=1)
    new_age = st.number_input("Age", min_value=18, max_value=100, step=1)
    new_dept = st.selectbox("Department", options=sorted(df['Department'].unique().tolist()))
    new_role = st.selectbox("Job Role", options=sorted(df['JobRole'].unique().tolist()))
    new_income = st.number_input("Monthly Income", min_value=1000, step=100)
    
    submitted = st.form_submit_button("Add Employee")
    if submitted:
        try:
            # Basic validation
            if new_id and new_age and new_dept and new_role and new_income:
                query = """
                INSERT INTO employees (EmployeeID, Age, Department, JobRole, MonthlyIncome, Attrition, Gender, Overtime, PerformanceRating) 
                VALUES (?, ?, ?, ?, ?, 'No', 'N/A', 'No', 3)
                """
                execute_query(query, (new_id, new_age, new_dept, new_role, new_income))
                st.sidebar.success(f"Employee {new_id} added successfully!")
                # NEW: Force the app to rerun to show the new entry immediately
                st.rerun()
            else:
                st.sidebar.error("Please fill all fields.")
        except sqlite3.IntegrityError:
             st.sidebar.error(f"Employee ID {new_id} already exists.")
        except Exception as e:
            st.sidebar.error(f"An error occurred: {e}")

# 3. Update Employee Income
with st.sidebar.form("update_income_form", clear_on_submit=True):
    st.subheader("Update Employee Income")
    emp_to_update = st.selectbox(
        "Select Employee ID to Update",
        options=sorted(df['EmployeeID'].unique().tolist())
    )
    new_monthly_income = st.number_input("New Monthly Income", min_value=1000, step=100)
    
    update_submitted = st.form_submit_button("Update Income")
    if update_submitted:
        try:
            query = "UPDATE employees SET MonthlyIncome = ? WHERE EmployeeID = ?"
            execute_query(query, (new_monthly_income, emp_to_update))
            st.sidebar.success(f"Income for Employee ID {emp_to_update} updated!")
            # NEW: Force the app to rerun to show the updated income
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Failed to update income: {e}")

# --- Main Dashboard ---
st.title(f"📊 HR Analytics Dashboard: {department}")
st.image("https://placehold.co/1200x200/4F008C/FFFFFF?text=HR+Analytics+Insights", use_container_width=True)

# --- Key Metrics (KPIs) ---
total_employees = df_filtered.shape[0]
avg_income = int(df_filtered['MonthlyIncome'].mean())
attrition_rate = (df_filtered[df_filtered['Attrition'] == 'Yes'].shape[0] / total_employees * 100) if total_employees > 0 else 0

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="Total Employees", value=f"{total_employees}")
kpi2.metric(label="Average Monthly Income", value=f"${avg_income:,}")
kpi3.metric(label="Attrition Rate", value=f"{attrition_rate:.2f}%")

st.markdown("---")

# --- NEW: TABS for better organization ---
tab1, tab2, tab3 = st.tabs(["Department Overview", "Attrition Deep Dive", "Employee Details"])

with tab1:
    st.header("Department Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar Chart: Employee Count by Job Role
        st.subheader("Employee Count by Job Role")
        role_counts = df_filtered['JobRole'].value_counts().reset_index()
        role_counts.columns = ['JobRole', 'Count']
        
        fig_bar = px.bar(
            role_counts, x='Count', y='JobRole', orientation='h',
            title=f"Distribution of Job Roles",
            color_discrete_sequence=['#4F008C']
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Bar Chart: Performance Rating Distribution
        st.subheader("Performance Rating Distribution")
        perf_counts = df_filtered['PerformanceRating'].value_counts().reset_index()
        perf_counts.columns = ['PerformanceRating', 'Count']
        
        fig_perf = px.bar(
            perf_counts, x='PerformanceRating', y='Count',
            title="Count of Employees by Performance Rating",
            color_discrete_sequence=['#FF375E']
        )
        st.plotly_chart(fig_perf, use_container_width=True)

    st.subheader("Income vs. Job Satisfaction")
    
    # FIX: The 'size' parameter for the scatter plot cannot handle missing values (NaN).
    # We create a temporary, cleaned dataframe by dropping rows where 'YearsAtCompany' is null
    # before passing it to the plotting function. This resolves the ValueError.
    scatter_df = df_filtered.dropna(subset=['YearsAtCompany'])

    fig_scatter = px.scatter(
        scatter_df, x='MonthlyIncome', y='JobSatisfaction',
        color='PerformanceRating',
        title="Income vs. Job Satisfaction, Colored by Performance",
        size='YearsAtCompany', hover_name='JobRole'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.header("Attrition Deep Dive")
    st.subheader("Investigating Why Employees Leave")

    col1, col2 = st.columns(2)

    with col1:
        # Pie Chart: Attrition Breakdown
        st.subheader("Overall Attrition Breakdown")
        attrition_counts = df_filtered['Attrition'].value_counts().reset_index()
        attrition_counts.columns = ['Attrition', 'Count']
        
        fig_pie = px.pie(
            attrition_counts, names='Attrition', values='Count',
            title=f"Attrition Breakdown",
            hole=0.4,
            color='Attrition',
            color_discrete_map={'Yes': '#FF375E', 'No': '#4F008C'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # NEW CHART: Attrition by Overtime
        st.subheader("Attrition Rate by Overtime")
        overtime_attrition = df_filtered.groupby('OverTime')['Attrition'].value_counts(normalize=True).unstack().fillna(0)
        if 'Yes' in overtime_attrition.columns:
            overtime_attrition = (overtime_attrition['Yes'] * 100).reset_index()
            overtime_attrition.columns = ['OverTime', 'Attrition Rate (%)']
            fig_overtime = px.bar(
                overtime_attrition, x='OverTime', y='Attrition Rate (%)',
                title="Overtime vs. Attrition Rate",
                color_discrete_sequence=['#FF375E']
            )
            st.plotly_chart(fig_overtime, use_container_width=True)
        else:
            st.info("No attrition data available for the selected overtime criteria.")

    st.markdown("---")
    # NEW CHART: Attrition by Performance Rating
    st.subheader("Are We Losing Our Top Performers?")
    perf_attrition = df_filtered.groupby(['PerformanceRating', 'Attrition']).size().reset_index(name='Count')
    
    fig_perf_attr = px.bar(
        perf_attrition, x='PerformanceRating', y='Count', color='Attrition',
        title='Attrition Count by Performance Rating',
        barmode='group',
        color_discrete_map={'Yes': '#FF375E', 'No': '#4F008C'}
    )
    st.plotly_chart(fig_perf_attr, use_container_width=True)


with tab3:
    st.header("Employee Details")
    st.subheader("Browse and Search Raw Data")
    # Display a subset of columns for clarity
    display_columns = [
        'EmployeeID', 'Age', 'Department', 'JobRole', 'MonthlyIncome',
        'PerformanceRating', 'JobSatisfaction', 'YearsAtCompany', 'Attrition', 'OverTime'
    ]
    
    # NEW: Dynamically calculate the height of the dataframe to prevent the last row from being cut off.
    # We'll calculate a height based on 35 pixels per row plus one for the header.
    # We'll also set a maximum height to prevent the table from becoming too long.
    df_for_display = df_filtered[display_columns]
    num_rows = len(df_for_display)
    dynamic_height = min((num_rows + 1) * 35, 600) # Max height of 600px

    st.dataframe(df_for_display, use_container_width=True, height=dynamic_height)


