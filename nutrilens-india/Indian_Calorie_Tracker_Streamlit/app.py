import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Indian Calorie Tracker",
    page_icon="🍛",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATASET_PATH = Path(__file__).parent / "Anuvaad_INDB_2024.11.xlsx"

# ── TEMPLATE ENGINE ───────────────────────────────────────────────────────────
# Each question has id, label, options, and per-option multipliers.
# The final portion = unit_serving_value × product_of_all_multipliers.

TEMPLATES = {
    "DOSA": {
        "label": "Dosa",
        "icon": "🫓",
        "questions": [
            {
                "id": "count",
                "label": "How many dosas?",
                "options": ["Half", "One", "Two", "Three"],
                "multipliers": {"Half": 0.5, "One": 1.0, "Two": 2.0, "Three": 3.0},
            },
            {
                "id": "prep",
                "label": "Preparation",
                "options": ["Homemade", "Restaurant", "Street Food"],
                "multipliers": {"Homemade": 0.95, "Restaurant": 1.10, "Street Food": 1.05},
            },
        ],
    },
    "IDLI": {
        "label": "Idli",
        "icon": "⚪",
        "questions": [
            {
                "id": "count",
                "label": "How many idlis?",
                "options": ["1", "2", "3", "4"],
                "multipliers": {"1": 1.0, "2": 2.0, "3": 3.0, "4": 4.0},
            },
            {
                "id": "size",
                "label": "Size",
                "options": ["Small", "Medium", "Large"],
                "multipliers": {"Small": 0.75, "Medium": 1.0, "Large": 1.30},
            },
        ],
    },
    "VADA": {
        "label": "Vada / Vadai",
        "icon": "🍩",
        "questions": [
            {
                "id": "count",
                "label": "How many vadas?",
                "options": ["1", "2", "3", "4"],
                "multipliers": {"1": 1.0, "2": 2.0, "3": 3.0, "4": 4.0},
            },
            {
                "id": "prep",
                "label": "Preparation",
                "options": ["Homemade", "Restaurant", "Street Food"],
                "multipliers": {"Homemade": 0.95, "Restaurant": 1.10, "Street Food": 1.05},
            },
        ],
    },
    "BIRYANI": {
        "label": "Biryani",
        "icon": "🍛",
        "questions": [
            {
                "id": "size",
                "label": "Serving Size",
                "options": ["Small Bowl", "Medium Bowl", "Large Bowl"],
                "multipliers": {"Small Bowl": 0.75, "Medium Bowl": 1.0, "Large Bowl": 1.50},
            },
        ],
    },
    "RICE": {
        "label": "Rice",
        "icon": "🍚",
        "questions": [
            {
                "id": "quantity",
                "label": "Quantity",
                "options": ["Quarter Plate", "Half Plate", "Full Plate"],
                "multipliers": {"Quarter Plate": 0.5, "Half Plate": 1.0, "Full Plate": 2.0},
            },
        ],
    },
    "BEVERAGE": {
        "label": "Beverage",
        "icon": "☕",
        "questions": [
            {
                "id": "size",
                "label": "Cup / Glass Size",
                "options": ["Small", "Medium", "Large"],
                "multipliers": {"Small": 0.75, "Medium": 1.0, "Large": 1.50},
            },
            {
                "id": "sugar",
                "label": "Sugar",
                "options": ["No Sugar", "1 tsp", "2 tsp", "3 tsp"],
                "multipliers": {"No Sugar": 1.0, "1 tsp": 1.06, "2 tsp": 1.12, "3 tsp": 1.18},
            },
        ],
    },
    "DAL": {
        "label": "Dal / Sambar / Soup",
        "icon": "🍲",
        "questions": [
            {
                "id": "quantity",
                "label": "Quantity",
                "options": ["Few Spoons", "Half Bowl", "Full Bowl"],
                "multipliers": {"Few Spoons": 0.5, "Half Bowl": 1.0, "Full Bowl": 2.0},
            },
            {
                "id": "prep",
                "label": "Preparation",
                "options": ["Homemade", "Restaurant"],
                "multipliers": {"Homemade": 0.95, "Restaurant": 1.10},
            },
        ],
    },
    "BREAD": {
        "label": "Roti / Bread",
        "icon": "🫓",
        "questions": [
            {
                "id": "count",
                "label": "How many?",
                "options": ["1", "2", "3", "4", "5"],
                "multipliers": {"1": 1.0, "2": 2.0, "3": 3.0, "4": 4.0, "5": 5.0},
            },
            {
                "id": "size",
                "label": "Size",
                "options": ["Small", "Medium", "Large"],
                "multipliers": {"Small": 0.80, "Medium": 1.0, "Large": 1.25},
            },
        ],
    },
    "CURRY": {
        "label": "Curry / Stir Fry",
        "icon": "🫕",
        "questions": [
            {
                "id": "quantity",
                "label": "Quantity",
                "options": ["Few Spoons", "Half Bowl", "Full Bowl"],
                "multipliers": {"Few Spoons": 0.5, "Half Bowl": 1.0, "Full Bowl": 2.0},
            },
            {
                "id": "prep",
                "label": "Preparation",
                "options": ["Homemade", "Restaurant"],
                "multipliers": {"Homemade": 0.95, "Restaurant": 1.10},
            },
        ],
    },
    "SNACK": {
        "label": "Snack",
        "icon": "🧆",
        "questions": [
            {
                "id": "quantity",
                "label": "Quantity",
                "options": ["Small Portion", "Medium Portion", "Large Portion"],
                "multipliers": {"Small Portion": 0.5, "Medium Portion": 1.0, "Large Portion": 1.5},
            },
        ],
    },
    "SWEET": {
        "label": "Sweet / Dessert",
        "icon": "🍮",
        "questions": [
            {
                "id": "quantity",
                "label": "Quantity",
                "options": ["Half", "One", "Two"],
                "multipliers": {"Half": 0.5, "One": 1.0, "Two": 2.0},
            },
            {
                "id": "prep",
                "label": "Preparation",
                "options": ["Homemade", "Mithai Shop", "Restaurant"],
                "multipliers": {"Homemade": 0.95, "Mithai Shop": 1.0, "Restaurant": 1.10},
            },
        ],
    },
    "FRUIT": {
        "label": "Fruit",
        "icon": "🍎",
        "questions": [
            {
                "id": "quantity",
                "label": "Quantity",
                "options": ["Half", "One", "Two", "Three"],
                "multipliers": {"Half": 0.5, "One": 1.0, "Two": 2.0, "Three": 3.0},
            },
        ],
    },
    "VEGETABLE": {
        "label": "Vegetable",
        "icon": "🥦",
        "questions": [
            {
                "id": "quantity",
                "label": "Quantity",
                "options": ["Few Spoons", "Half Bowl", "Full Bowl"],
                "multipliers": {"Few Spoons": 0.5, "Half Bowl": 1.0, "Full Bowl": 2.0},
            },
            {
                "id": "prep",
                "label": "Preparation",
                "options": ["Raw / Salad", "Cooked"],
                "multipliers": {"Raw / Salad": 1.0, "Cooked": 0.90},
            },
        ],
    },
    "NON_VEG": {
        "label": "Non Veg",
        "icon": "🍗",
        "questions": [
            {
                "id": "quantity",
                "label": "Quantity",
                "options": ["Small Portion", "Half Bowl", "Full Bowl"],
                "multipliers": {"Small Portion": 0.75, "Half Bowl": 1.0, "Full Bowl": 1.50},
            },
            {
                "id": "prep",
                "label": "Preparation",
                "options": ["Homemade", "Restaurant"],
                "multipliers": {"Homemade": 0.95, "Restaurant": 1.10},
            },
        ],
    },
    "GENERAL": {
        "label": "Food Item",
        "icon": "🍽️",
        "questions": [
            {
                "id": "quantity",
                "label": "Quantity",
                "options": ["Small", "Medium", "Large"],
                "multipliers": {"Small": 0.75, "Medium": 1.0, "Large": 1.50},
            },
        ],
    },
}

# ── CATEGORY CLASSIFIER ───────────────────────────────────────────────────────
CATEGORY_RULES = [
    ("DOSA",      ["dosa", "dosai", "uttapam", "uttappam", "pesarattu"]),
    ("IDLI",      ["idli", "idly"]),
    ("VADA",      ["vada", "vadai", "vade"]),
    ("BIRYANI",   ["biryani", "biriyani"]),
    ("BEVERAGE",  ["tea", "coffee", "juice", "milk", "lassi", "buttermilk", "shake",
                   "smoothie", "chai", "kaapi", "sherbet", "lemonade", "soda", "cocoa",
                   "cooler", "aam panna", "milkshake", "eggnog", "squash", "punch",
                   "drink", "water"]),
    ("DAL",       ["sambar", "rasam", "dal", "dhal", "daal", "soup", "lentil", "paruppu"]),
    ("BREAD",     ["chapati", "chapathi", "roti", "paratha", "parantha", "naan", "puri",
                   "poori", "parotta", "appam", "pathiri", "bhatura", "kulcha", "thepla",
                   "puttu", "cheela", "bread", "toast", "sandwich", "roll", "pav"]),
    ("RICE",      ["rice", "pulao", "pulav", "pongal", "khichdi", "khichri", "sadam",
                   "chawal", "anna", "upma", "poha", "murmura", "chivda", "biryani"]),
    ("NON_VEG",   ["chicken", "mutton", "fish", "egg", "prawn", "beef", "pork", "meat",
                   "keema", "crab", "seafood", "lamb", "shrimp", "tuna", "mackerel"]),
    ("SWEET",     ["halwa", "halva", "kheer", "payasam", "ladoo", "laddoo", "barfi",
                   "burfi", "mithai", "cake", "pudding", "ice cream", "kulfi",
                   "gulab jamun", "rasgulla", "jalebi", "peda", "modak", "mysore pak",
                   "sweet", "candy", "chocolate", "toffee"]),
    ("FRUIT",     ["apple", "banana", "mango", "orange", "grape", "guava", "papaya",
                   "watermelon", "pineapple", "pomegranate", "lychee", "jackfruit",
                   "fruit", "pear", "plum", "strawberry", "cherry", "fig", "date"]),
    ("SNACK",     ["biscuit", "chips", "murukku", "chakli", "popcorn", "mixture",
                   "namkeen", "mathri", "bhujia", "pakoda", "pakora", "bajji", "bonda",
                   "samosa", "puff", "khakhra", "thattai", "ribbon", "cutlet", "tikki"]),
    ("CURRY",     ["curry", "masala", "poriyal", "thoran", "sabzi", "sabji", "bhaji",
                   "gravy", "roast", "stir fry", "palak", "paneer", "korma", "vindaloo",
                   "kootu", "stew", "fry"]),
    ("VEGETABLE", ["vegetable", "greens", "salad", "spinach", "carrot", "beans", "peas",
                   "broccoli", "cauliflower", "cabbage", "yam", "drumstick",
                   "brinjal", "eggplant"]),
]

# ── SMART SUGGESTIONS ─────────────────────────────────────────────────────────
MEAL_SUGGESTIONS = {
    "idli":          ["Sambar", "Coconut chutney", "Hot tea (Garam Chai)"],
    "dosa":          ["Sambar", "Coconut chutney", "Hot tea (Garam Chai)"],
    "masala dosa":   ["Sambar", "Coconut chutney"],
    "uttapam":       ["Sambar", "Coconut chutney", "Hot tea (Garam Chai)"],
    "pongal":        ["Sambar", "Coconut chutney", "Plain urad dal vada"],
    "vada":          ["Sambar", "Coconut chutney"],
    "sambar":        ["Boiled rice (Uble chawal)", "Idli", "Plain dosa"],
    "rice":          ["Sambar", "Boiled rice (Uble chawal)", "Curd rice"],
    "biryani":       ["Raita", "Salan"],
    "chapati":       ["Dal", "Curd"],
    "roti":          ["Dal", "Curd"],
    "paratha":       ["Curd", "Pickle"],
    "upma":          ["Coconut chutney", "Hot tea (Garam Chai)"],
    "poha":          ["Hot tea (Garam Chai)", "Curd"],
}

QUICK_MEALS = {
    "🌅 South Indian Breakfast": ["Idli", "Sambar", "Hot tea (Garam Chai)"],
    "🍽️ Tamil Nadu Lunch":       ["Boiled rice (Uble chawal)", "Sambar", "Curd rice (Dahi bhaat/Dahi chawal/ Perugu annam/Daddojanam/Thayir saadam)"],
    "🫓 North Indian Dinner":    ["Chapati/Roti", "Dal", "Curd"],
    "🫕 Mini Tiffin":            ["Idli", "Plain urad dal vada (Uzunne vada/Minapa garelu/Ulundu vadai/Medu vada)", "Sambar"],
    "🥘 Street Breakfast":       ["Masala dosa", "Sambar", "Hot tea (Garam Chai)"],
}

# Nutrient columns used for display
MACRO_DISPLAY = [
    ("energy_kcal",  "unit_serving_energy_kcal",  "Calories",  "kcal", "#FF6B35"),
    ("protein_g",    "unit_serving_protein_g",     "Protein",   "g",    "#4CAF50"),
    ("carb_g",       "unit_serving_carb_g",        "Carbs",     "g",    "#2196F3"),
    ("fat_g",        "unit_serving_fat_g",         "Fat",       "g",    "#FF9800"),
    ("fibre_g",      "unit_serving_fibre_g",       "Fibre",     "g",    "#8BC34A"),
    ("freesugar_g",  "unit_serving_freesugar_g",   "Free Sugar","g",    "#E91E63"),
]

MICRO_DISPLAY = [
    ("calcium_mg",   "unit_serving_calcium_mg",   "Calcium",    "mg"),
    ("iron_mg",      "unit_serving_iron_mg",       "Iron",       "mg"),
    ("vitc_mg",      "unit_serving_vitc_mg",       "Vitamin C",  "mg"),
    ("potassium_mg", "unit_serving_potassium_mg",  "Potassium",  "mg"),
    ("sodium_mg",    "unit_serving_sodium_mg",     "Sodium",     "mg"),
    ("magnesium_mg", "unit_serving_magnesium_mg",  "Magnesium",  "mg"),
    ("zinc_mg",      "unit_serving_zinc_mg",       "Zinc",       "mg"),
    ("phosphorus_mg","unit_serving_phosphorus_mg", "Phosphorus", "mg"),
    ("folate_ug",    "unit_serving_folate_ug",     "Folate",     "μg"),
    ("vitb1_mg",     "unit_serving_vitb1_mg",      "Vitamin B1", "mg"),
    ("vitb2_mg",     "unit_serving_vitb2_mg",      "Vitamin B2", "mg"),
    ("vitb3_mg",     "unit_serving_vitb3_mg",      "Niacin B3",  "mg"),
    ("vitd3_ug",     "unit_serving_vitd3_ug",      "Vitamin D3", "μg"),
]


# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading INDB dataset…")
def load_data():
    df = pd.read_excel(DATASET_PATH)
    df.columns = [c.strip() for c in df.columns]
    df["food_name"] = df["food_name"].astype(str).str.strip()
    return df


# ── FOOD CLASSIFIER ───────────────────────────────────────────────────────────
def classify_food(name: str) -> str:
    n = name.lower()
    for template_id, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in n:
                return template_id
    return "GENERAL"


# ── NUTRITION CALCULATOR ──────────────────────────────────────────────────────
def calc_nutrition(row: pd.Series, answers: dict, template_id: str) -> dict:
    """Apply template multipliers to unit_serving_* values."""
    tmpl = TEMPLATES[template_id]
    multiplier = 1.0
    for q in tmpl["questions"]:
        ans = answers.get(q["id"])
        if ans:
            multiplier *= q["multipliers"].get(ans, 1.0)

    nutrition = {}
    for per100_col, unit_col, label, unit, _ in MACRO_DISPLAY:
        base = row.get(unit_col)
        if pd.isna(base):
            base = row.get(per100_col, 0) or 0
        nutrition[label] = round(float(base) * multiplier, 1)

    for per100_col, unit_col, label, unit in MICRO_DISPLAY:
        base = row.get(unit_col)
        if pd.isna(base):
            base = row.get(per100_col, 0) or 0
        nutrition[label] = round(float(base) * multiplier, 2)

    return nutrition


# ── HEALTH SCORES ─────────────────────────────────────────────────────────────
def health_scores(nutrition: dict, daily_goal: int = 2000) -> dict:
    cal    = nutrition.get("Calories", 0)
    protein = nutrition.get("Protein", 0)
    carbs  = nutrition.get("Carbs", 0)
    fibre  = nutrition.get("Fibre", 0)
    sugar  = nutrition.get("Free Sugar", 0)
    fat    = nutrition.get("Fat", 0)

    # Weight Loss: low calorie density + high fibre
    cal_pct   = min(1.0, cal / (daily_goal * 0.35))
    wl = max(0, min(100, int(100 - cal_pct * 60 + min(20, fibre * 2) - min(20, fat * 0.5))))

    # Muscle Gain: protein ratio
    mg = min(100, int((protein / max(cal, 1)) * 400)) if cal > 0 else 0

    # Diabetic Friendly: low sugar + moderate carbs + high fibre
    sugar_pen = min(40, sugar * 5)
    carb_pen  = min(30, max(0, (carbs - 40) * 0.8))
    fibre_bon = min(20, fibre * 2)
    db = max(0, min(100, int(80 - sugar_pen - carb_pen + fibre_bon)))

    return {"Weight Loss": wl, "Muscle Gain": mg, "Diabetic Friendly": db}


# ── SESSION STATE ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "meal_items": [],
        "saved_meals": {},
        "daily_goal": 2000,
        "meal_type": "Breakfast",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown(
        """
        <style>
        /* Global */
        .block-container { padding-top: 1.5rem; }

        /* Food card */
        .food-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #FF6B35;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 8px;
        }
        .food-card-name { font-weight: 700; font-size: 1rem; color: #1a202c; }
        .food-card-meta { font-size: 0.82rem; color: #718096; margin-top: 2px; }
        .food-card-kcal { font-weight: 600; color: #FF6B35; }

        /* Nutrition pill */
        .nut-pill {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 4px;
        }
        .nut-cal  { background:#FFF0EB; color:#FF6B35; }
        .nut-prot { background:#EDFBEE; color:#38A169; }
        .nut-carb { background:#EBF4FF; color:#3182CE; }
        .nut-fat  { background:#FFF8E1; color:#D69E2E; }

        /* Section header */
        .section-head {
            font-size: 1.15rem;
            font-weight: 700;
            color: #2D3748;
            margin-bottom: 8px;
            border-bottom: 2px solid #FF6B35;
            padding-bottom: 4px;
        }

        /* Meal type badge */
        .meal-badge {
            display: inline-block;
            background: #FF6B35;
            color: white;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        /* Score bar */
        .score-bar-wrap { margin: 4px 0; }
        .score-label { font-size: 0.8rem; color: #4A5568; margin-bottom: 2px; }

        /* Quick template button */
        div[data-testid="stButton"] button {
            border-radius: 8px;
        }

        /* Hide Streamlit brand */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── TOTAL NUTRITION ───────────────────────────────────────────────────────────
def sum_nutrition(items: list) -> dict:
    total = {}
    for item in items:
        for k, v in item["nutrition"].items():
            total[k] = round(total.get(k, 0) + v, 1)
    return total


# ── SUGGESTION LOOKUP ─────────────────────────────────────────────────────────
def get_suggestions(food_name: str) -> list:
    n = food_name.lower()
    for kw, suggs in MEAL_SUGGESTIONS.items():
        if kw in n:
            return suggs
    return []


# ── TRACK MEAL TAB ────────────────────────────────────────────────────────────
def render_track_tab(df: pd.DataFrame):
    # ── Meal type selector
    st.markdown('<div class="section-head">Step 1 — Select Meal Type</div>', unsafe_allow_html=True)
    meal_type = st.radio(
        "",
        ["🌅 Breakfast", "☀️ Lunch", "🌙 Dinner", "🫐 Snacks", "☕ Beverages"],
        horizontal=True,
        key="meal_type_radio",
        label_visibility="collapsed",
    )
    st.session_state.meal_type = meal_type.split()[-1]

    # Quick meal templates
    with st.expander("⚡ Quick Meal Templates — add a full set in one click"):
        tcols = st.columns(len(QUICK_MEALS))
        for col, (name, foods) in zip(tcols, QUICK_MEALS.items()):
            if col.button(name, use_container_width=True, key=f"qm_{name}"):
                st.session_state["quick_add_queue"] = foods
                st.rerun()

    # Handle quick-add queue
    if "quick_add_queue" in st.session_state and st.session_state["quick_add_queue"]:
        queue = st.session_state["quick_add_queue"]
        for food_name in queue:
            matches = df[df["food_name"].str.lower() == food_name.lower()]
            if not matches.empty:
                row = matches.iloc[0]
                template_id = classify_food(food_name)
                tmpl = TEMPLATES[template_id]
                default_answers = {q["id"]: q["options"][1 if len(q["options"]) > 1 else 0]
                                   for q in tmpl["questions"]}
                nutrition = calc_nutrition(row, default_answers, template_id)
                st.session_state.meal_items.append({
                    "food_name": food_name,
                    "template_id": template_id,
                    "answers": default_answers,
                    "nutrition": nutrition,
                    "servings_unit": str(row.get("servings_unit", "")),
                })
        del st.session_state["quick_add_queue"]
        st.rerun()

    st.divider()

    left, right = st.columns([1, 1], gap="large")

    # ── LEFT: Food Search + Form ───────────────────────────────────────────
    with left:
        st.markdown('<div class="section-head">Step 2 — Add Food</div>', unsafe_allow_html=True)

        query = st.text_input(
            "Search food",
            placeholder="Type to search… e.g. Masala Dosa, Idli, Sambar",
            key="food_search_input",
        )

        if query and len(query) >= 2:
            mask = df["food_name"].str.lower().str.contains(query.lower(), na=False)
            results = df[mask]["food_name"].tolist()[:20]

            if not results:
                st.warning("No foods matched. Try a different term.")
            else:
                selected_food = st.selectbox("Results", results, key="food_select_box")

                if selected_food:
                    row = df[df["food_name"] == selected_food].iloc[0]
                    template_id = classify_food(selected_food)
                    tmpl = TEMPLATES[template_id]

                    st.caption(
                        f"Category: **{tmpl['icon']} {tmpl['label']}** · "
                        f"Serving unit: **{row.get('servings_unit', 'N/A')}**"
                    )

                    answers = {}
                    for q in tmpl["questions"]:
                        answers[q["id"]] = st.radio(
                            q["label"],
                            q["options"],
                            horizontal=True,
                            key=f"q_{selected_food}_{q['id']}",
                        )

                    # Live preview
                    preview = calc_nutrition(row, answers, template_id)
                    p1, p2, p3, p4 = st.columns(4)
                    p1.metric("Calories", f"{preview['Calories']} kcal")
                    p2.metric("Protein",  f"{preview['Protein']}g")
                    p3.metric("Carbs",    f"{preview['Carbs']}g")
                    p4.metric("Fat",      f"{preview['Fat']}g")

                    if st.button("➕ Add to Meal", type="primary", use_container_width=True, key="add_food_btn"):
                        st.session_state.meal_items.append({
                            "food_name": selected_food,
                            "template_id": template_id,
                            "answers": answers.copy(),
                            "nutrition": preview,
                            "servings_unit": str(row.get("servings_unit", "")),
                        })
                        # Clear search so next food can be typed
                        st.rerun()
        elif not query:
            st.caption("Start typing to search from 1,014 Indian foods.")

    # ── RIGHT: Meal Cart ───────────────────────────────────────────────────
    with right:
        items = st.session_state.meal_items
        badge = st.session_state.meal_type
        st.markdown(
            f'<div class="section-head">Step 3 — Current Meal &nbsp; '
            f'<span class="meal-badge">{badge}</span></div>',
            unsafe_allow_html=True,
        )

        if not items:
            st.info("Your meal is empty. Add foods from the left panel.")
        else:
            # Food cards
            for i, item in enumerate(items):
                n = item["nutrition"]
                ans_str = "  ·  ".join(str(v) for v in item["answers"].values())
                st.markdown(
                    f"""
                    <div class="food-card">
                      <div class="food-card-name">{item['food_name']}</div>
                      <div class="food-card-meta">{ans_str}</div>
                      <div style="margin-top:6px">
                        <span class="nut-pill nut-cal">{n['Calories']} kcal</span>
                        <span class="nut-pill nut-prot">P {n['Protein']}g</span>
                        <span class="nut-pill nut-carb">C {n['Carbs']}g</span>
                        <span class="nut-pill nut-fat">F {n['Fat']}g</span>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("🗑 Remove", key=f"rm_{i}_{item['food_name']}", help="Remove this item"):
                    st.session_state.meal_items.pop(i)
                    st.rerun()

            st.divider()

            # Totals
            total = sum_nutrition(items)
            goal  = st.session_state.daily_goal
            tc, tp, tcarb, tf = st.columns(4)
            tc.metric("Total Calories", f"{round(total.get('Calories',0))} kcal")
            tp.metric("Protein",  f"{round(total.get('Protein',0),1)}g")
            tcarb.metric("Carbs", f"{round(total.get('Carbs',0),1)}g")
            tf.metric("Fat",      f"{round(total.get('Fat',0),1)}g")

            pct = min(1.0, total.get("Calories", 0) / goal)
            st.progress(pct, text=f"{round(total.get('Calories',0))} / {goal} kcal daily goal")

            # Health Scores
            st.markdown("**Health Scores**")
            scores = health_scores(total, goal)
            score_colors = {
                "Weight Loss": "#FF6B35",
                "Muscle Gain": "#38A169",
                "Diabetic Friendly": "#3182CE",
            }
            scols = st.columns(3)
            for col, (name, val) in zip(scols, scores.items()):
                color = score_colors[name]
                col.markdown(
                    f"<div style='text-align:center'>"
                    f"<div style='font-size:1.6rem;font-weight:800;color:{color}'>{val}</div>"
                    f"<div style='font-size:0.75rem;color:#718096'>{name}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            # Smart suggestions
            if items:
                last_name = items[-1]["food_name"]
                suggestions = get_suggestions(last_name)
                if suggestions:
                    st.markdown("**You might also add:**")
                    sug_cols = st.columns(len(suggestions))
                    for col, s in zip(sug_cols, suggestions):
                        col.caption(f"➕ {s}")

            # Save / Clear
            st.divider()
            s1, s2 = st.columns([3, 1])
            save_name = s1.text_input("Save meal as", placeholder="e.g. My Breakfast", key="save_name_input")
            if s2.button("💾 Save", use_container_width=True) and save_name:
                st.session_state.saved_meals[save_name] = {
                    "meal_type": badge,
                    "items": [
                        {"food_name": it["food_name"], "answers": it["answers"], "nutrition": it["nutrition"]}
                        for it in items
                    ],
                    "total": total,
                }
                st.success(f"Saved: **{save_name}**")

            if st.button("🗑 Clear Meal", use_container_width=True):
                st.session_state.meal_items = []
                st.rerun()


# ── NUTRITION REPORT TAB ──────────────────────────────────────────────────────
def render_nutrition_report():
    st.markdown('<div class="section-head">Nutrition Report — Current Meal</div>',
                unsafe_allow_html=True)

    items = st.session_state.meal_items
    if not items:
        st.info("Add foods in the Track Meal tab to see the nutrition report.")
        return

    total = sum_nutrition(items)

    # Macro summary table
    macro_rows = []
    for _, _, label, unit, color in MACRO_DISPLAY:
        macro_rows.append({"Nutrient": label, "Amount": total.get(label, 0), "Unit": unit})
    macro_df = pd.DataFrame(macro_rows)
    macro_df["Amount"] = macro_df["Amount"].round(1)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("Macronutrients")
        st.dataframe(
            macro_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Nutrient": st.column_config.TextColumn("Nutrient"),
                "Amount":   st.column_config.NumberColumn("Amount", format="%.1f"),
                "Unit":     st.column_config.TextColumn("Unit"),
            },
        )

        # Calorie breakdown bar chart
        st.subheader("Calorie Sources")
        cal_from_protein = total.get("Protein", 0) * 4
        cal_from_carb    = total.get("Carbs", 0)   * 4
        cal_from_fat     = total.get("Fat", 0)     * 9
        chart_df = pd.DataFrame({
            "Source": ["Protein", "Carbohydrates", "Fat"],
            "Calories": [cal_from_protein, cal_from_carb, cal_from_fat],
        })
        st.bar_chart(chart_df.set_index("Source"), color="#FF6B35")

    with col2:
        st.subheader("Micronutrients")
        micro_rows = []
        for _, _, label, unit in MICRO_DISPLAY:
            val = total.get(label, 0)
            if val > 0:
                micro_rows.append({"Nutrient": label, "Amount": val, "Unit": unit})
        if micro_rows:
            micro_df = pd.DataFrame(micro_rows)
            st.dataframe(
                micro_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Nutrient": st.column_config.TextColumn("Nutrient"),
                    "Amount":   st.column_config.NumberColumn("Amount", format="%.2f"),
                    "Unit":     st.column_config.TextColumn("Unit"),
                },
            )

        # Health Scores
        st.subheader("Health Scores")
        scores = health_scores(total, st.session_state.daily_goal)
        for name, val in scores.items():
            bar_color = "#FF6B35" if val < 40 else "#F6AD55" if val < 70 else "#48BB78"
            st.markdown(f"**{name}**: {val} / 100")
            st.progress(val / 100)

    # Per-food breakdown
    st.subheader("Per-Food Breakdown")
    rows = []
    for item in items:
        n = item["nutrition"]
        rows.append({
            "Food": item["food_name"],
            "Calories": n.get("Calories", 0),
            "Protein(g)": n.get("Protein", 0),
            "Carbs(g)": n.get("Carbs", 0),
            "Fat(g)": n.get("Fat", 0),
            "Fibre(g)": n.get("Fibre", 0),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ── SAVED MEALS TAB ───────────────────────────────────────────────────────────
def render_saved_meals():
    st.markdown('<div class="section-head">Saved Meals</div>', unsafe_allow_html=True)

    saved = st.session_state.saved_meals
    if not saved:
        st.info("No saved meals yet. Build a meal and click 💾 Save.")
        return

    for name, data in list(saved.items()):
        total = data["total"]
        with st.expander(
            f"**{name}** · {data['meal_type']} · "
            f"{round(total.get('Calories',0))} kcal · "
            f"P {total.get('Protein',0)}g · C {total.get('Carbs',0)}g · F {total.get('Fat',0)}g"
        ):
            for it in data["items"]:
                n = it["nutrition"]
                ans_str = "  ·  ".join(str(v) for v in it["answers"].values())
                st.markdown(
                    f"""
                    <div class="food-card">
                      <div class="food-card-name">{it['food_name']}</div>
                      <div class="food-card-meta">{ans_str}</div>
                      <div style="margin-top:5px">
                        <span class="nut-pill nut-cal">{n['Calories']} kcal</span>
                        <span class="nut-pill nut-prot">P {n['Protein']}g</span>
                        <span class="nut-pill nut-carb">C {n['Carbs']}g</span>
                        <span class="nut-pill nut-fat">F {n['Fat']}g</span>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            lc, rc = st.columns([1, 1])
            if lc.button("🔄 Load into Meal Builder", key=f"load_{name}", use_container_width=True):
                st.session_state.meal_items = [
                    {
                        "food_name": it["food_name"],
                        "template_id": classify_food(it["food_name"]),
                        "answers": it["answers"],
                        "nutrition": it["nutrition"],
                        "servings_unit": "",
                    }
                    for it in data["items"]
                ]
                st.success(f"Loaded **{name}** into meal builder.")
                st.rerun()

            if rc.button("🗑 Delete", key=f"del_saved_{name}", use_container_width=True):
                del st.session_state.saved_meals[name]
                st.rerun()


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    inject_css()
    init_state()

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_India.svg/320px-Flag_of_India.svg.png", width=80)
        st.title("🍛 Indian Calorie Tracker")
        st.caption("Powered by INDB 2024 — 1,014 Indian foods")
        st.divider()

        st.subheader("🎯 Daily Goal")
        st.session_state.daily_goal = st.number_input(
            "Calorie target (kcal)", 800, 5000,
            st.session_state.daily_goal, 50,
            key="daily_goal_input",
        )

        # Today's progress
        total_cal = sum(it["nutrition"].get("Calories", 0) for it in st.session_state.meal_items)
        goal = st.session_state.daily_goal
        pct = min(1.0, total_cal / goal)
        st.divider()
        st.subheader("📊 Today's Progress")
        st.progress(pct, text=f"{round(total_cal)} / {goal} kcal")
        remaining = max(0, goal - total_cal)
        st.caption(f"Remaining: **{round(remaining)} kcal**")
        st.caption(f"Foods added: **{len(st.session_state.meal_items)}**")

        st.divider()
        st.caption("INDB — Anuvaad 2024.11 dataset")

    # ── Main content ─────────────────────────────────────────────────────────
    st.markdown("## 🍛 Indian Calorie Tracker")

    df = load_data()

    tab1, tab2, tab3 = st.tabs([
        "🍽️ Track Meal",
        "📊 Nutrition Report",
        "💾 Saved Meals",
    ])

    with tab1:
        render_track_tab(df)

    with tab2:
        render_nutrition_report()

    with tab3:
        render_saved_meals()


if __name__ == "__main__" or True:
    main()
