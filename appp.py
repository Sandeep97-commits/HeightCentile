import streamlit as st
import pandas as pd

# ---------- Data Loader ----------
@st.cache_data
def load_height_csv(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()  # remove spaces
    if "Age (years)" in df.columns:
        df.set_index("Age (years)", inplace=True)
    else:
        df = pd.read_csv(path, header=1, encoding="utf-8-sig")
        df.set_index("Age (years)", inplace=True)
    df.index = pd.to_numeric(df.index, errors="coerce")
    df = df[~df.index.isna()]
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.dropna(axis=1, how="all")
    return df

# Load CSV files
boys_df = load_height_csv("height_boys.csv")
girls_df = load_height_csv("Height_girls.csv")

# ---------- Function ----------
def get_centiles(age, gender, height):
    df = boys_df if gender.lower().startswith('b') else girls_df
    age = float(age)

    # --- Round age using round() ---
    age_years = round(age)

    # --- Select closest age row ---
    available_ages = df.index.values.astype(float)
    closest_age = min(available_ages, key=lambda x: abs(x - age_years))
    row = df.loc[closest_age].astype(float)

    # --- Calculate differences (with signs) ---
    diffs = row - height
    abs_diffs = diffs.abs()
    min_diff = abs_diffs.min()

    # --- Get all centiles with the same minimum difference ---
    closest_centiles = abs_diffs[abs_diffs == min_diff].index.tolist()
    closest_heights = [row[c] for c in closest_centiles]

    # Return list of tuples: (centile, height)
    return list(zip(closest_centiles, closest_heights))

# ---------- Streamlit UI ----------
st.title("Height Centile Calculator")

age = st.number_input("Age (years):", min_value=1.0, max_value=17.0, step=0.1)
gender = st.radio("Gender:", ["Boy", "Girl"])
height = st.number_input("Height (cm):", min_value=50.0, max_value=200.0, step=0.1)

# --- Reactive output ---
results = get_centiles(age, gender, height)

if results:
    if len(results) == 1:
        centile, val = results[0]
        st.success(f"Nearest centile: {centile} ({val:.1f} cm)")
    else:
        msg = "Nearest centiles: " + ", ".join([f"{c} ({v:.1f} cm)" for c, v in results])
        st.success(msg)
else:
    st.error("Age out of dataset range.")
