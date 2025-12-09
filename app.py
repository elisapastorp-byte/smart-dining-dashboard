import streamlit as st
import pandas as pd
import pulp as pl
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Smart Dining on Campus",
    page_icon="🍽️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E40AF;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None
if 'results' not in st.session_state:
    st.session_state.results = None

# Header
st.markdown('<div class="main-header">🍽️ Smart Dining on Campus</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your personalized weekly meal optimization system</div>', unsafe_allow_html=True)

# Progress bar
progress_col1, progress_col2, progress_col3 = st.columns(3)
with progress_col1:
    st.markdown(f"**{'✅' if st.session_state.step >= 1 else '⭕'} Step 1: Upload Data**")
with progress_col2:
    st.markdown(f"**{'✅' if st.session_state.step >= 2 else '⭕'} Step 2: Preferences**")
with progress_col3:
    st.markdown(f"**{'✅' if st.session_state.step >= 3 else '⭕'} Step 3: Results**")

st.markdown("---")

# ==================== STEP 1: UPLOAD CSV ====================
if st.session_state.step == 1:
    st.header("📤 Step 1: Upload Your Meal Database")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file with your meal data",
        type=['csv'],
        help="Upload a CSV file containing meal information with nutritional data"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.csv_data = df
            
            st.success(f"✅ File loaded successfully! {len(df)} meals available.")
            
            with st.expander("📊 Preview Data"):
                st.dataframe(df.head(10))
            
            if st.button("Continue to Preferences ➡️", key="continue_step1"):
                st.session_state.step = 2
                st.rerun()
                
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

# ==================== STEP 2: PREFERENCES ====================
elif st.session_state.step == 2:
    st.header("⚙️ Step 2: Set Your Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏥 Health & Allergies")
        diabetic = st.checkbox("Diabetic")
        celiac = st.checkbox("Celiac (Gluten Intolerant)")
        lactose_intolerant = st.checkbox("Lactose Intolerant")
        nut_allergy = st.checkbox("Nut Allergy")
        
        st.subheader("🥗 Diet Type")
        vegan = st.checkbox("Vegan")
        vegetarian = st.checkbox("Vegetarian")
        pescatarian = st.checkbox("Pescatarian")
        keto = st.checkbox("Keto")
        
        st.subheader("🕌 Religious/Cultural")
        kosher = st.checkbox("Kosher")
        halal = st.checkbox("Halal")
    
    with col2:
        st.subheader("🎯 Health Goals")
        gain_weight = st.checkbox("Gain Weight")
        lose_weight = st.checkbox("Lose Weight")
        gain_muscle = st.checkbox("Gain Muscle")
        
        st.subheader("🍽️ Food Preferences")
        avoid_grains = st.checkbox("Avoid Grains")
        avoid_legumes = st.checkbox("Avoid Legumes")
        avoid_bread = st.checkbox("Avoid Bread")
        avoid_dairy = st.checkbox("Avoid Dairy")
        avoid_spicy = st.checkbox("Avoid Spicy Food")
        avoid_fried = st.checkbox("Avoid Fried Food")
        
        st.subheader("⚙️ Basic Settings")
        gender = st.selectbox("Gender", ["male", "female", "other"])
        budget = st.slider("Weekly Budget ($)", 50, 300, 100, 5)
    
    st.markdown("---")
    col_back, col_optimize = st.columns([1, 2])
    
    with col_back:
        if st.button("⬅️ Back to Upload"):
            st.session_state.step = 1
            st.rerun()
    
    with col_optimize:
        if st.button("🚀 Generate Optimal Plan", key="optimize_btn"):
            with st.spinner("Optimizing your meal plan... This may take a few seconds."):
                try:
                    # Store preferences
                    preferences = {
                        'diabetic': diabetic, 'celiac': celiac, 'lactose_intolerant': lactose_intolerant,
                        'nut_allergy': nut_allergy, 'vegan': vegan, 'vegetarian': vegetarian,
                        'pescatarian': pescatarian, 'keto': keto, 'kosher': kosher, 'halal': halal,
                        'gain_weight': gain_weight, 'lose_weight': lose_weight, 'gain_muscle': gain_muscle,
                        'avoid_grains': avoid_grains, 'avoid_legumes': avoid_legumes, 'avoid_bread': avoid_bread,
                        'avoid_dairy': avoid_dairy, 'avoid_spicy': avoid_spicy, 'avoid_fried': avoid_fried,
                        'gender': gender, 'budget': budget
                    }
                    
                    # Run optimization
                    results = run_optimization(st.session_state.csv_data, preferences)
                    st.session_state.results = results
                    st.session_state.step = 3
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Optimization failed: {str(e)}")
                    st.info("Try relaxing some constraints or increasing your budget.")

# ==================== STEP 3: RESULTS ====================
elif st.session_state.step == 3 and st.session_state.results is not None:
    st.header("📊 Your Optimized Weekly Meal Plan")
    
    results = st.session_state.results
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Cost", f"${results['total_cost']:.2f}", 
                 f"{results['budget_used']:.1f}% of budget")
    with col2:
        st.metric("🔥 Avg Calories/Day", f"{results['avg_calories']:.0f}")
    with col3:
        st.metric("💪 Avg Protein/Day", f"{results['avg_protein']:.1f}g")
    with col4:
        st.metric("✅ Total Meals", "14")
    
    st.markdown("---")
    
    # Weekly plan
    st.subheader("📅 Your Weekly Schedule")
    
    plan_df = pd.DataFrame(results['plan'])
    
    # Show by day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day in days:
        st.markdown(f"### {day}")
        day_meals = plan_df[plan_df['day'] == day]
        
        col_lunch, col_dinner = st.columns(2)
        
        with col_lunch:
            lunch = day_meals[day_meals['meal_type'] == 'Lunch'].iloc[0] if len(day_meals[day_meals['meal_type'] == 'Lunch']) > 0 else None
            if lunch is not None:
                st.markdown(f"""
                **🌅 LUNCH**  
                **{lunch['dish']}**  
                📍 {lunch['restaurant']}  
                💵 ${lunch['price']:.2f} | 🔥 {lunch['calories']:.0f} kcal | 💪 {lunch['protein']:.1f}g protein
                """)
        
        with col_dinner:
            dinner = day_meals[day_meals['meal_type'] == 'Dinner'].iloc[0] if len(day_meals[day_meals['meal_type'] == 'Dinner']) > 0 else None
            if dinner is not None:
                st.markdown(f"""
                **🌙 DINNER**  
                **{dinner['dish']}**  
                📍 {dinner['restaurant']}  
                💵 ${dinner['price']:.2f} | 🔥 {dinner['calories']:.0f} kcal | 💪 {dinner['protein']:.1f}g protein
                """)
        
        st.markdown("---")
    
    # Charts
    st.subheader("📈 Nutritional Analysis")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Daily calories chart
        daily_stats = plan_df.groupby('day').agg({'calories': 'sum'}).reset_index()
        daily_stats['day'] = pd.Categorical(daily_stats['day'], categories=days, ordered=True)
        daily_stats = daily_stats.sort_values('day')
        
        fig_cal = px.bar(daily_stats, x='day', y='calories', 
                        title='Daily Calories',
                        labels={'calories': 'Calories (kcal)', 'day': 'Day'},
                        color='calories',
                        color_continuous_scale='Blues')
        st.plotly_chart(fig_cal, use_container_width=True)
    
    with chart_col2:
        # Daily protein chart
        daily_protein = plan_df.groupby('day').agg({'protein': 'sum'}).reset_index()
        daily_protein['day'] = pd.Categorical(daily_protein['day'], categories=days, ordered=True)
        daily_protein = daily_protein.sort_values('day')
        
        fig_prot = px.bar(daily_protein, x='day', y='protein',
                         title='Daily Protein',
                         labels={'protein': 'Protein (g)', 'day': 'Day'},
                         color='protein',
                         color_continuous_scale='Greens')
        st.plotly_chart(fig_prot, use_container_width=True)
    
    # Export button
    st.markdown("---")
    csv_export = plan_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Plan as CSV",
        data=csv_export,
        file_name="weekly_meal_plan.csv",
        mime="text/csv"
    )
    
    # Action buttons
    col_modify, col_restart = st.columns(2)
    with col_modify:
        if st.button("⬅️ Modify Preferences"):
            st.session_state.step = 2
            st.rerun()
    with col_restart:
        if st.button("🔄 Start Over"):
            st.session_state.step = 1
            st.session_state.csv_data = None
            st.session_state.results = None
            st.rerun()


# ==================== OPTIMIZATION FUNCTION ====================
def run_optimization(df, preferences):
    """Run the meal plan optimization"""
    
    filtered = df.copy()
    
    # Apply filters
    if preferences['diabetic']:
        filtered = filtered[filtered['diabetic_friendly'] == 1]
    if preferences['celiac']:
        filtered = filtered[filtered['contains_gluten'] == 0]
    if preferences['lactose_intolerant']:
        filtered = filtered[filtered['contains_lactose'] == 0]
    if preferences['nut_allergy']:
        filtered = filtered[filtered['contains_nuts'] == 0]
    if preferences['vegan']:
        filtered = filtered[filtered['vegan'] == 1]
    if preferences['vegetarian']:
        filtered = filtered[filtered['vegetarian'] == 1]
    if preferences['pescatarian']:
        filtered = filtered[filtered['pescatarian'] == 1]
    if preferences['keto']:
        filtered = filtered[filtered['keto_friendly'] == 1]
    if preferences['kosher']:
        filtered = filtered[filtered['kosher'] == 1]
    if preferences['halal']:
        filtered = filtered[filtered['halal'] == 1]
    if preferences['gain_weight']:
        filtered = filtered[filtered['gaining_weight_diet'] == 1]
    if preferences['lose_weight']:
        filtered = filtered[filtered['loose_weight_diet'] == 1]
    if preferences['gain_muscle']:
        filtered = filtered[filtered['gaining_muscle_diet'] == 1]
    if preferences['avoid_grains']:
        filtered = filtered[filtered['contains_grains'] == 0]
    if preferences['avoid_legumes']:
        filtered = filtered[filtered['contains_legumes'] == 0]
    if preferences['avoid_bread']:
        filtered = filtered[filtered['contains_bread'] == 0]
    if preferences['avoid_dairy']:
        filtered = filtered[filtered['contains_dairy'] == 0]
    if preferences['avoid_spicy']:
        filtered = filtered[filtered['spicy'] == 0]
    if preferences['avoid_fried']:
        filtered = filtered[filtered['fried'] == 0]
    
    if len(filtered) < 14:
        raise Exception(f"Not enough meals after filtering. Only {len(filtered)} meals available. Need at least 14.")
    
    # Reset index
    filtered = filtered.reset_index(drop=True)
    meal_indices = list(filtered.index)
    
    days = range(7)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meals = ["Lunch", "Dinner"]
    restaurants = filtered["Restaurant"].unique().tolist()
    
    # Nutritional targets
    if preferences['gender'] == "male":
        cal_min, cal_max = 1100, 1600
        protein_min = 50
    elif preferences['gender'] == "female":
        cal_min, cal_max = 900, 1400
        protein_min = 45
    else:
        cal_min, cal_max = 1000, 1500
        protein_min = 45
    
    # Create optimization problem
    prob = pl.LpProblem("WeeklyMealPlan", pl.LpMinimize)
    
    # Decision variables
    x = {}
    for i in meal_indices:
        for d in days:
            for m in meals:
                x[(i, d, m)] = pl.LpVariable(f"x_{i}_{d}_{m}", cat="Binary")
    
    # Objective: minimize cost
    total_cost = pl.lpSum(
        filtered.loc[i, "price"] * x[(i, d, m)]
        for i in meal_indices for d in days for m in meals
    )
    prob += total_cost
    
    # Budget constraint
    prob += total_cost <= preferences['budget'], "BudgetConstraint"
    
    # Exactly 1 meal per (day, meal type)
    for d in days:
        for m in meals:
            prob += pl.lpSum(x[(i, d, m)] for i in meal_indices) == 1, f"OneMeal_day{d}_{m}"
    
    # Each dish max once per week
    for i in meal_indices:
        prob += pl.lpSum(x[(i, d, m)] for d in days for m in meals) <= 1, f"UniqueMeal_{i}"
    
    # Max 5 meals from same restaurant per week
    for r in restaurants:
        prob += pl.lpSum(
            x[(i, d, m)]
            for i in meal_indices for d in days for m in meals
            if filtered.loc[i, "Restaurant"] == r
        ) <= 5, f"MaxRestaurantWeek_{r}"
    
    # Solve
    prob.solve(pl.PULP_CBC_CMD(msg=0))
    
    if pl.LpStatus[prob.status] != "Optimal":
        raise Exception("Could not find optimal solution. Try relaxing constraints or increasing budget.")
    
    # Extract results
    plan = []
    for d in days:
        for m in meals:
            for i in meal_indices:
                if pl.value(x[(i, d, m)]) > 0.5:
                    row = filtered.loc[i]
                    plan.append({
                        'day': day_names[d],
                        'meal_type': m,
                        'restaurant': row['Restaurant'],
                        'dish': row['Meal'],
                        'price': row['price'],
                        'calories': row['calories_kcal'],
                        'protein': row['protein_g']
                    })
    
    plan_df = pd.DataFrame(plan)
    actual_cost = plan_df['price'].sum()
    avg_calories = plan_df.groupby('day')['calories'].sum().mean()
    avg_protein = plan_df.groupby('day')['protein'].sum().mean()
    
    return {
        'plan': plan,
        'total_cost': actual_cost,
        'budget_used': (actual_cost / preferences['budget']) * 100,
        'avg_calories': avg_calories,
        'avg_protein': avg_protein
    }
