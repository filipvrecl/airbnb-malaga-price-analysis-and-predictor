import streamlit as st
import joblib
import numpy as np
import pandas as pd

# Load trained pipeline (preprocessing + XGBoost)
pipe = joblib.load("airbnb_price_model.pkl")

st.title("Málaga Airbnb Price Predictor")
st.write("Enter listing details below to predict the estimated nightly price.")

# USER INPUT WIDGETS

# --- 1. Listing Basics ---
st.header("Listing Basics")
neighbourhood_options = [
    'Campanillas', 'Churriana', 'Puerto de la Torre', 'Este',
    'Teatinos-Universidad', 'Carretera de Cadiz', 'Cruz De Humilladero',
    'Bailen-Miraflores', 'Centro', 'Palma-Palmilla', 'Ciudad Jardin'
]
property_type_options = [
    'Entire rental unit', 'Private room in rental unit', 'Entire condo',
    'Entire home', 'Entire serviced apartment', 'Entire loft',
    'Private room in home', 'Entire vacation home', 'Entire villa',
    'Entire townhouse', 'Private room in condo', 'Room in hotel', 'Camper/RV'
]
room_type_options = ["Entire home/apt", "Private room", "Shared room"]

neighbourhood = st.selectbox("Neighbourhood", neighbourhood_options)
property_type = st.selectbox("Property Type", property_type_options)
room_type = st.selectbox("Room Type", room_type_options)

accommodates = st.number_input("Accommodates", min_value=1, max_value=16, value=2)
bedrooms = st.number_input("Bedrooms", min_value=0, max_value=10, value=1)
beds = st.number_input("Beds", min_value=0, max_value=10, value=1)
bathrooms = st.number_input("Bathrooms", min_value=0.0, max_value=10.0, value=1.0, step=0.5)

# --- 2. Host Details ---
st.header("Host Details")
host_responses = ["within an hour", "within a day", "a few days or more", "within a few hours"]
host_response_time = st.selectbox("Host Response Time", host_responses)

host_total_listings_count = st.number_input("Number of Host's Total Listings", min_value=1, max_value=50, value=1)
host_is_superhost = int(st.checkbox("Is the Host a Superhost?"))
host_identity_verified = int(st.checkbox("Is the Host's Identity Verified?"))
instant_bookable = int(st.checkbox("Instantly Bookable?"))

# --- 3. Performance & Quality ---
st.header("Performance & Quality")
review_score_mean = st.slider("Average Review Score (0-10)", 0.0, 10.0, 8.0)
estimated_occupancy_l365d = st.slider("Estimated Occupancy Last 365 Days (%)", 0, 100, 50)
fall_avail_rate = st.slider("Fall Availability Rate (%)", 0, 100, 50)
winter_avail_rate = st.slider("Winter Availability Rate (%)", 0, 100, 50)
host_engagement_score = st.slider("Host Engagement Score (0-1)", 0.0, 1.0, 0.5)

# --- PREDICTION ---
if st.button("Predict Price"):
    # Compute hidden features
    has_availability = 1  # Always assume available
    is_multi_host = int(host_total_listings_count > 1)

    # Build DataFrame for a single sample
    X_new = pd.DataFrame([{
        'neighbourhood_cleansed': neighbourhood,
        'property_type': property_type,
        'room_type': room_type,
        'accommodates': accommodates,
        'bathrooms': bathrooms,
        'bedrooms': bedrooms,
        'beds': beds,
        'host_response_time': host_response_time,
        'host_is_superhost': host_is_superhost,
        'host_total_listings_count': host_total_listings_count,
        'host_identity_verified': host_identity_verified,
        'instant_bookable': instant_bookable,
        'has_availability': has_availability,
        'estimated_occupancy_l365d': estimated_occupancy_l365d,
        'fall_avail_rate': fall_avail_rate,
        'winter_avail_rate': winter_avail_rate,
        'is_multi_host': is_multi_host,
        'host_engagement_score': host_engagement_score,
        'review_score_mean': review_score_mean
    }])

    # Neighbourhood averages (from earlier analysis)
    neighbourhood_avg_prices = {
        'Campanillas': 965.59,
        'Churriana': 678.68,
        'Puerto de la Torre': 402.56,
        'Este': 354.04,
        'Teatinos-Universidad': 241.68,
        'Carretera de Cadiz': 230.70,
        'Cruz De Humilladero': 225.58,
        'Bailen-Miraflores': 220.39,
        'Centro': 168.12,
        'Palma-Palmilla': 167.93,
        'Ciudad Jardin': 111.08
    }
    neighbourhood_avg = neighbourhood_avg_prices.get(neighbourhood, None)

    # Predict log-price and convert
    log_price_pred = pipe.predict(X_new)[0]
    price_pred = np.expm1(log_price_pred)

    # Add confidence range using known average error (~30%)
    lower_bound = price_pred * (1 - 0.30)
    upper_bound = price_pred * (1 + 0.30)

    st.success(f"Predicted nightly price: ${price_pred:.2f}")
    st.info(f"Typical range (based on similar listings): ${lower_bound:.2f} - {upper_bound:.2f}")

    if neighbourhood_avg:
            st.write(f"Average price in {neighbourhood}: **${neighbourhood_avg:.2f}**")
            if price_pred > neighbourhood_avg:
                st.write("Your listing is predicted to be **above** the neighbourhood average.")
            else:
                st.write("Your listing is predicted to be **below** the neighbourhood average.")