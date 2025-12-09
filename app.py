import streamlit as st
import pandas as pd
import pulp as pl
import plotly.express as px
import plotly.graph_objects as go
import os

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

# Required columns
REQUIRED_COLUMNS = ['Restaurant', 'Meal', 'price', 'calories_kcal', 'protein_g', 'fat_g', 
                   'sugar_g', 'contains_gluten', 'contains_lactose', 'diabetic_friendly', 
                   'vegan ', 'vegetarian', 'pescatarian', 'kosher', 'halal', 'contains_nuts', 
                   'contains_lactose.1', 'carbs_g', 'calcium_mg', 'fiber_mg', 'cholesterol_mg', 
                   'potassium_mg', 'iron_mg', 'sodium_mg', 'contains_grains', 'contains_legumes', 
                   'contains_bread', 'contains_dairy', 'keto_friendly', 'gaining_weight_diet', 
                   'loose_weight_diet', 'gaining_muscle_diet', 'spicy', 'fried', 'grilled ', 
                   'baked', 'boiled']

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'using_default' not in st.session_state:
    st.session_state.using_default = False

# Function to load default CSV
def load_default_csv():
    """Try to load the default CSV file"""
    try:
        if os.path.exists('lunchplandef3.csv'):
            return pd.read_csv('lunchplandef3.csv')
        else:
            return None
    except Exception as e:
        st.error(f"Error loading default database: {str(e)}")
        return None

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
    
    st.info("💡 **Tip**: You can upload your own CSV file or use our default meal database to get started immediately!")
    
    # Show required columns in expander
    with st.expander("📋 Required CSV Columns (Click to expand)"):
        st.write("**Your CSV must contain ALL of these columns:**")
        cols_display = st.columns(3)
        for idx, col in enumerate(REQUIRED_COLUMNS):
            with cols_display[idx % 3]:
                st.write(f"• `{col}`")
        st.warning("⚠️ Column names must match exactly (including spaces and capitalization)")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Upload Your Own CSV")
        uploaded_file = st.file_uploader(
            "Choose a CSV file with your meal data",
            type=['csv'],
            help="Upload a CSV file containing meal information with nutritional data"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Validate columns
                missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ **Missing required columns ({len(missing_cols)}):**")
                    for col in missing_cols[:10]:  # Show first 10
                        st.write(f"   • `{col}`")
                    if len(missing_cols) > 10:
                        st.write(f"   ... and {len(missing_cols) - 10} more")
                    st.warning("Please ensure your CSV has all required columns or use the default database.")
                else:
                    st.session_state.csv_data = df
                    st.session_state.using_default = False
                    st.success(f"✅ File loaded successfully! {len(df)} meals available.")
                    
                    with st.expander("📊 Preview Your Data"):
                        st.dataframe(df.head(10))
                    
                    if st.button("Continue to Preferences ➡️", key="continue_uploaded"):
                        st.session_state.step = 2
                        st.rerun()
                        
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    with col2:
        st.subheader("Use Default Database")
        st.write("Skip the upload and use our pre-loaded meal database")
        
        if st.button("🚀 Use Default Meal Database", key="use_default", type="primary"):
            default_df = load_default_csv()
            
            if default_df is not None:
                st.session_state.csv_data = default_df
                st.session_state.using_default = True
                st.success(f"✅ Default database loaded! {len(default_df)} meals available.")
                
                # Auto-advance to next step after 1 second
                if st.button("Continue to Preferences ➡️", key="continue_default"):
                    st.session_state.step = 2
                    st.rerun()
            else:
                st.error("❌ Default database not found!")
                st.info("""
                **To enable the default database:**
                1. Upload your `lunchplandef3.csv` to your GitHub repository
                2. Place it in the same folder as `app.py`
                3. Commit the changes
                4. Streamlit will automatically detect it
                
                For now, please upload your CSV using the option on the left.
                """)

# ==================== STEP 2: PREFERENCES ====================
elif st.session_state.step == 2:
    st.header("⚙️ Step 2: Set Your Preferences")
    
    if st.session_state.using_default:
        st.success("📊 Using default meal database")
    else:
        st.info(f"📊 Using uploaded database with {len(st.session_state.csv_data)} meals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏥 Health & Allergies")
        diabetic = st.checkbox("Diabetic", help="Filter meals suitable for diabetics")
        celiac = st.checkbox("Celiac (Gluten Intolerant)", help="Exclude meals containing gluten")
        lactose_intolerant = st.checkbox("Lactose Intolerant", help="Exclude meals with lactose")
        nut_allergy = st.checkbox("Nut Allergy", help="Exclude meals containing nuts")
        
        st.subheader("🥗 Diet Type")
        vegan = st.checkbox("Vegan", help="Only plant-based meals")
        vegetarian = st.checkbox("Vegetarian", help="No meat, but dairy/eggs OK")
        pescatarian = st.checkbox("Pescatarian", help="Fish OK, no other meat")
        keto = st.checkbox("Keto", help="Low-carb, high-fat diet")
        
        st.subheader("🕌 Religious/Cultural")
        kosher = st.checkbox("Kosher", help="Meals prepared according to Jewish law")
        halal = st.checkbox("Halal", help="Meals prepared according to Islamic law")
    
    with col2:
        st.subheader("🎯 Health Goals")
        gain_weight = st.checkbox("Gain Weight", help="Higher calorie meals")
        lose_weight = st.checkbox("Lose Weight", help="Lower calorie meals")
        gain_muscle = st.checkbox("Gain Muscle", help="High protein meals")
        
        st.subheader("🍽️ Food Preferences")
        avoid_grains = st.checkbox("Avoid Grains", help="No rice, wheat, oats, etc.")
        avoid_legumes = st.checkbox("Avoid Legumes", help="No beans, lentils, peas")
        avoid_bread = st.checkbox("Avoid Bread", help="No bread products")
        avoid_dairy = st.checkbox("Avoid Dairy", help="No milk, cheese, yogurt")
        avoid_spicy = st.checkbox("Avoid Spicy Food", help="No hot/spicy dishes")
        avoid_fried = st.checkbox("Avoid Fried Food", help="No fried preparations")
        
        st.subheader("⚙️ Basic Settings")
        gender = st.selectbox("Gender", ["male", "female", "other"], 
                             help="Affects nutritional targets")
        budget = st.slider("Weekly Budget ($)", 50, 300, 100, 5,
                          help="Maximum amount to spend on meals per week")
        
        st.caption(f"💰 Selected budget: **${budget}** for 14 meals")
    
    st.markdown("---")
    col_back, col_optimize = st.columns([1, 2])
    
    with col_back:
        if st.button("⬅️ Back to Upload"):
            st.session_state.step = 1
            st.rerun()
    
    with col_optimize:
        if st.button("🚀 Generate Optimal Plan", key="optimize_btn", type="primary"):
            if st.session_state.csv_data is None:
                st.error("❌ Please upload a CSV file first or use the default database.")
            else:
                with st.spinner("🔄 Optimizing your meal plan... This may take 10-30 seconds."):
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
                        st.info("💡 **Suggestions:**")
                        st.write("• Try increasing your budget")
                        st.write("• Relax some dietary restrictions")
                        st.write("• Ensure your CSV has enough meal variety")

# ==================== STEP 3: RESULTS ====================
elif st.session_state.step == 3 and st.session_state.results is not None:
    st.header("📊 Your Optimized Weekly Meal Plan")
    
    results = st.session_state.results
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_budget = results['budget_used'] - 100
        st.metric("💰 Total Cost", f"${results['total_cost']:.2f}", 
                 f"{results['budget_used']:.1f}% of budget",
                 delta_color="inverse")
    with col2:
        st.metric("🔥 Avg Calories/Day", f"{results['avg_calories']:.0f}")
    with col3:
        st.metric("💪 Avg Protein/Day", f"{results['avg_protein']:.1f}g")
    with col4:
        st.metric("✅ Total Meals", "14", "2 per day")
    
    st.markdown("---")
    
    # Weekly plan
    st.subheader("📅 Your Weekly Schedule")
    
    plan_df = pd.DataFrame(results['plan'])
    
    # Show by day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day in days:
        with st.container():
            st.markdown(f"### 📆 {day}")
            day_meals = plan_df[plan_df['day'] == day]
            
            col_lunch, col_dinner = st.columns(2)
            
            with col_lunch:
                lunch = day_meals[day_meals['meal_type'] == 'Lunch']
                if len(lunch) > 0:
                    lunch = lunch.iloc[0]
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 1.5rem; border-radius: 10px; color: white;">
                        <h4>🌅 LUNCH</h4>
                        <h3>{lunch['dish']}</h3>
                        <p>📍 {lunch['restaurant']}</p>
                        <hr style="border-color: white; opacity: 0.3;">
                        <p>💵 ${lunch['price']:.2f} | 🔥 {lunch['calories']:.0f} kcal | 💪 {lunch['protein']:.1f}g</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_dinner:
                dinner = day_meals[day_meals['meal_type'] == 'Dinner']
                if len(dinner) > 0:
                    dinner = dinner.iloc[0]
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                padding: 1.5rem; border-radius: 10px; color: white;">
                        <h4>🌙 DINNER</h4>
                        <h3>{dinner['dish']}</h3>
                        <p>📍 {dinner['restaurant']}</p>
                        <hr style="border-color: white; opacity: 0.3;">
                        <p>💵 ${dinner['price']:.2f} | 🔥 {dinner['calories']:.0f} kcal | 💪 {dinner['protein']:.1f}g</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
    
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
                        title='Daily Calories Distribution',
                        labels={'calories': 'Calories (kcal)', 'day': 'Day'},
                        color='calories',
                        color_continuous_scale='Blues')
        fig_cal.update_layout(showlegend=False)
        st.plotly_chart(fig_cal, use_container_width=True)
    
    with chart_col2:
        # Daily protein chart
        daily_protein = plan_df.groupby('day').agg({'protein': 'sum'}).reset_index()
        daily_protein['day'] = pd.Categorical(daily_protein['day'], categories=days, ordered=True)
        daily_protein = daily_protein.sort_values('day')
        
        fig_prot = px.bar(daily_protein, x='day', y='protein',
                         title='Daily Protein Distribution',
                         labels={'protein': 'Protein (g)', 'day': 'Day'},
                         color='protein',
                         color_continuous_scale='Greens')
        fig_prot.update_layout(showlegend=False)
        st.plotly_chart(fig_prot, use_container_width=True)
    
    # Restaurant distribution
    st.subheader("🏪 Restaurant Variety")
    restaurant_counts = plan_df['restaurant'].value_counts().reset_index()
    restaurant_counts.columns = ['Restaurant', 'Meals']
    
    fig_rest = px.pie(restaurant_counts, values='Meals', names='Restaurant',
                      title='Meals per Restaurant',
                      color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig_rest, use_container_width=True)
    
    # Export button
    st.markdown("---")
    st.subheader("📥 Export Your Plan")
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        csv_export = plan_df.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv_export,
            file_name="weekly_meal_plan.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_export2:
        # Summary text
        summary = f"""
WEEKLY MEAL PLAN SUMMARY
========================
Total Cost: ${results['total_cost']:.2f}
Budget Used: {results['budget_used']:.1f}%
Avg Daily Calories: {results['avg_calories']:.0f} kcal
Avg Daily Protein: {results['avg_protein']:.1f}g
Total Meals: 14 (2 per day)

Generated by Smart Dining on Campus
"""
        st.download_button(
            label="📝 Download Summary (TXT)",
            data=summary,
            file_name="meal_plan_summary.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Action buttons
    st.markdown("---")
    col_modify, col_restart = st.columns(2)
    with col_modify:
        if st.button("⬅️ Modify Preferences", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with col_restart:
        if st.button("🔄 Start Over", use_container_width=True):
            st.session_state.step = 1
            st.session_state.csv_data = None
            st.session_state.results = None
            st.session_state.using_default = False
            st.rerun()


# ==================== OPTIMIZATION FUNCTION ====================
def run_optimization(df, preferences):
    """Run the meal plan optimization using PuLP linear programming"""
    
    filtered = df.copy()
    
    # Apply filters based on preferences
    if preferences['diabetic']:
        filtered = filtered[filtered['diabetic_friendly'] == 1]
    if preferences['celiac']:
        filtered = filtered[filtered['contains_gluten'] == 0]
    if preferences['lactose_intolerant']:
        filtered = filtered[filtered['contains_lactose'] == 0]
    if preferences['nut_allergy']:
        filtered = filtered[filtered['contains_nuts'] == 0]
    if preferences['vegan']:
        filtered = filtered[filtered['vegan '] == 1]  # Note: space in column name
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
        raise Exception(f"Not enough meals after filtering. Only {len(filtered)} meals available. Need at least 14 meals to create a weekly plan.")
    
    # Reset index
    filtered = filtered.reset_index(drop=True)
    meal_indices = list(filtered.index)
    
    days = range(7)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meals = ["Lunch", "Dinner"]
    restaurants = filtered["Restaurant"].unique().tolist()
    
    # Nutritional targets based on gender
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
    
    # Decision variables: x[i,d,m] = 1 if meal i is chosen on day d for meal type m
    x = {}
    for i in meal_indices:
        for d in days:
            for m in meals:
                x[(i, d, m)] = pl.LpVariable(f"x_{i}_{d}_{m}", cat="Binary")
    
    # Objective function: minimize total cost
    total_cost = pl.lpSum(
        filtered.loc[i, "price"] * x[(i, d, m)]
        for i in meal_indices for d in days for m in meals
    )
    prob += total_cost
    
    # ==================== CONSTRAINTS ====================
    
    # C1: Budget constraint
    prob += total_cost <= preferences['budget'], "BudgetConstraint"
    
    # C2: Exactly 1 meal per (day, meal type)
    for d in days:
        for m in meals:
            prob += pl.lpSum(x[(i, d, m)] for i in meal_indices) == 1, f"OneMeal_day{d}_{m}"
    
    # C3: Each dish max once per week (no repeats)
    for i in meal_indices:
        prob += pl.lpSum(x[(i, d, m)] for d in days for m in meals) <= 1, f"UniqueMeal_{i}"
    
    # C4: Max 5 meals from same restaurant per week
    for r in restaurants:
        prob += pl.lpSum(
            x[(i, d, m)]
            for i in meal_indices for d in days for m in meals
            if filtered.loc[i, "Restaurant"] == r
        ) <= 5, f"MaxRestaurantWeek_{r}"
    
    # C5: Max 1 meal per restaurant per day
    for d in days:
        for r in restaurants:
            prob += pl.lpSum(
                x[(i, d, m)]
                for i in meal_indices for m in meals
                if filtered.loc[i, "Restaurant"] == r
            ) <= 1, f"MaxRestaurantDay_{d}_{r}"
    
    # C6: No legumes at dinner
    for d in days:
        prob += pl.lpSum(
            x[(i, d, "Dinner")]
            for i in meal_indices
            if filtered.loc[i, "contains_legumes"] == 1
        ) == 0, f"NoLegumesDinner_{d}"
    
    # C7: No grains at dinner
    for d in days:
        prob += pl.lpSum(
            x[(i, d, "Dinner")]
            for i in meal_indices
            if filtered.loc[i, "contains_grains"] == 1
        ) == 0, f"NoGrainsDinner_{d}"
    
    # Solve the optimization problem
    status = prob.solve(pl.PULP_CBC_CMD(msg=0))
    
    if pl.LpStatus[status] != "Optimal":
        raise Exception("Could not find optimal solution. Try increasing budget or relaxing some constraints.")
    
    # Extract solution
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
    
    # Calculate metrics
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
