"""
    This file includes data preparation for our analysis.
"""

from pathlib import Path
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)

# Accessing the file
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "data" / "listings.csv.gz"

# Load CSV
df = pd.read_csv(DATA_PATH)

""" 
    NOTE 1. Filtering columns
    Since the table has 79 columns, we need to snatch out the ones relevant to our goals.
    For this, we will use an SQL query (could just use Pandas instead)
"""

import sqlite3

# Create an in-memory SQLite database
conn = sqlite3.connect(':memory:')

# Write the full dataframe into an SQL table
df.to_sql('listings', conn, index=False, if_exists='replace')

# View columns (ran earlier)
# --> print(df.columns)

# List of columns to keep:
columns_to_keep = [
    # Basic info
    'id', 'name', 'description', 'host_id',

    # Location
    'neighbourhood_cleansed', 'latitude', 'longitude',

    # Room/property type
    'property_type', 'room_type', 'accommodates', 'bathrooms', 'bedrooms', 'beds', 'amenities',

    # Host characteristics
    'host_since', 'host_response_time', 'host_response_rate', 'host_acceptance_rate',
    'host_is_superhost', 'host_listings_count', 'host_total_listings_count',
    'host_identity_verified',

    # Review scores
    'review_scores_rating', 'review_scores_accuracy', 'review_scores_cleanliness',
    'review_scores_checkin', 'review_scores_communication',
    'review_scores_location', 'review_scores_value',
    'number_of_reviews', 'reviews_per_month',

    # Availability
    'instant_bookable', 'has_availability', 'availability_30', 'availability_60', 'availability_90', 'availability_365',
    'estimated_occupancy_l365d',

    # Price-related
    'price', 'minimum_nights', 'maximum_nights',

    # NOTE: Prices are normalized to be in $USD, even though we are located in Europe

    # Calendar and scrape timing
    'last_scraped', 'calendar_last_scraped'
]

columns_sql = ', '.join(columns_to_keep)

# SQL Query:
query = f"""
    SELECT {columns_sql}
    FROM listings
"""

# Save the filtered df and close connection
filtered_df = pd.read_sql_query(query, conn)
conn.close()

# We do not need to standardize column names, since they are already clean

# Clean price column:
filtered_df['price'] = filtered_df['price'].replace(r'[\$,]', '', regex=True).astype(float)


# Clean amenities:
    # Since it is a long string, we can simplify it by looking at count:
filtered_df['num_amenities'] = filtered_df['amenities'].str.count(',') + 1
filtered_df = filtered_df.drop(['amenities'], axis=1)


"""NOTE 2. Handling missing values"""

# After running print(filtered_df.isnull().sum()):

filtered_df['description'] = filtered_df['description'].fillna('No description provided')

# Replace missing discrete features with medians
filtered_df['bathrooms'] = filtered_df['bathrooms'].fillna(df['bathrooms'].median())
filtered_df['bedrooms'] = filtered_df['bedrooms'].fillna(df['bedrooms'].median())
filtered_df['beds'] = filtered_df['beds'].fillna(df['beds'].median())

# Replacing booleans
filtered_df = filtered_df.replace({'t': 1, 'f': 0})

# Logically replace with modus, since it dominates
filtered_df['host_is_superhost'] = filtered_df['host_is_superhost'].fillna(0) # Mostly not a superhost
filtered_df['host_response_time'] = filtered_df['host_response_time'].fillna('within an hour') # 95% of cases

# Turning into categorical column:
response_order = [
    'within an hour',
    'within a few hours',
    'within a day',
    'a few days or more',
    'unknown'
]
filtered_df['host_response_time'] = pd.Categorical(filtered_df['host_response_time'], categories=response_order, ordered=True)

# Converting the % in every column:
percent_cols = ['host_response_rate', 'host_acceptance_rate']

for col in percent_cols:
    filtered_df[col] = filtered_df[col].str.rstrip('%').astype(float) / 100

# Fill missing continious values with means,
# since we will probably do mean engineering with them later on_:
filtered_df['host_response_rate'] = filtered_df['host_response_rate'].fillna(filtered_df['host_response_rate'].mean())
filtered_df['host_acceptance_rate'] = filtered_df['host_acceptance_rate'].fillna(filtered_df['host_acceptance_rate'].mean())


# Same logic for all missing review score values
filtered_df['review_scores_rating'] = filtered_df['review_scores_rating'].fillna(filtered_df['review_scores_rating'].mean())
filtered_df['review_scores_accuracy'] = filtered_df['review_scores_accuracy'].fillna(filtered_df['review_scores_accuracy'].mean())
filtered_df['review_scores_cleanliness'] = filtered_df['review_scores_cleanliness'].fillna(filtered_df['review_scores_cleanliness'].mean())
filtered_df['review_scores_checkin'] = filtered_df['review_scores_checkin'].fillna(filtered_df['review_scores_checkin'].mean())
filtered_df['review_scores_communication'] = filtered_df['review_scores_communication'].fillna(filtered_df['review_scores_communication'].mean())
filtered_df['review_scores_location'] = filtered_df['review_scores_location'].fillna(filtered_df['review_scores_location'].mean())
filtered_df['review_scores_value'] = filtered_df['review_scores_value'].fillna(filtered_df['review_scores_value'].mean())
filtered_df['reviews_per_month'] = filtered_df['reviews_per_month'].fillna(filtered_df['reviews_per_month'].mean())


# Only 96 rows with missing info about has_availability (can afford to drop):
filtered_df = filtered_df.dropna(subset=['has_availability'])

# Price is our main goal, rows with missing price are useless:
filtered_df = filtered_df.dropna(subset=['price'])
# 8683 rows remaining


"""NOTE 3. Convert date columns into datetime"""

date_cols = ['last_scraped', 'calendar_last_scraped', 'host_since']
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')



"""NOTE 4. Check for price outliars"""

# 1 insanely high outliar, no use, getting rid of him
filtered_df = filtered_df[filtered_df['price'] < 10000]

import seaborn as sns
import matplotlib.pyplot as plt


# --> print(filtered_df[filtered_df['price'] > 1000]['price'])

# Motivates us for new luxury column:
filtered_df['is_luxury'] = filtered_df['price'] > 500

plt.figure(figsize=(10, 6))
sns.violinplot(x=filtered_df[filtered_df['is_luxury'] == False]['price'])

plt.title('Price Distribution of Airbnb Listings in Málaga')
plt.xlabel('Price (€)')
plt.tight_layout()
#plt.show()

#print(f"Total number of columns: {len(filtered_df)}")   --> 8682
#print(f"Luxury columns ignored on plot: {filtered_df["is_luxury"].sum()}")  --> 221



"""
    !  We also want to merge calendar with our dataframe (dates)
"""
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "data" / "calendar.csv.gz"

# Load CSV
calendar = pd.read_csv(DATA_PATH)


#print(calendar[calendar["listing_id"] == 1386113325037443875].head())
#print(calendar[calendar["listing_id"] == 1386113325037443875].shape)

""" NOTE:
    Since every listing_id is associated with its availability in the following year,
    this motivates us to create new features, based on seasonal availability.
    (This may impact price, since people probably like Malaga in the summer, for
    example)
"""

# Ensure date column is datetime
calendar['date'] = pd.to_datetime(calendar['date'])
# Math column name with original dataframe
calendar.rename({"listing_id" : "id"}, axis=1, inplace=True)

# Define seasons by month mapping
season_map = {
    'spring': [3, 4, 5],
    'summer': [6, 7, 8],
    'fall':   [9, 10, 11],
    'winter': [12, 1, 2]
}

# Function to calculate availability features per season
def seasonal_availability(df, season_name, months):
    mask = df['date'].dt.month.isin(months)
    return (
        df[mask]
        .groupby('id')
        .agg(
            **{
                f'{season_name}_avail_rate': ('available', lambda x: (x == 't').mean()),
                f'{season_name}_available': ('available', lambda x: int((x == 't').mean() > 0.5))
            }
        )
    )

# Build seasonal availability features
seasonal_features = []
for season, months in season_map.items():
    seasonal_features.append(seasonal_availability(calendar, season, months))

# Combine all seasons
seasonal_df = pd.concat(seasonal_features, axis=1).reset_index()

# Merge back into the original dataframe
filtered_df = filtered_df.merge(seasonal_df, on='id', how='left')



# Exporting back into CSV:
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEANED_PATH = PROJECT_ROOT / "data" / "listings_cleaned.csv"

# Save cleaned dataframe
filtered_df.to_csv(CLEANED_PATH, index=False)
print(f"Cleaned dataset saved to: {CLEANED_PATH}")

""" NOTE
    Our data is now cleaned, has no missing values, no unnecessary columns,
    which implies we are ready to move onto analysis.
"""