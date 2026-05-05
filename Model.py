import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
# ==============================
# CONFIG
# ==============================
FILE_PATH = "fpl_data_all_players_merged.xlsx"   # input data file
OUTPUT_PREDICTIONS = "fpl_predictions_trustworthy.xlsx"  # output file
OUTPUT_VALIDATION = "model_validation.xlsx"       # validation file

MIN_MINUTES = 20          # ignore players who played less than this
SPLIT_PERCENTILE = 0.8    # 80% train, 20% test
N_ESTIMATORS = 200        # number of trees in random forest
MAX_DEPTH = 8             # how deep each tree goes
MIN_SAMPLES_LEAF = 10     # minimum data points per prediction
RANDOM_STATE = 42         # keeps results consistent every run

# -------------------------------
# STEP 1: LOAD DATA
# -------------------------------
file_path = FILE_PATH

df = pd.read_excel(file_path, sheet_name="Merged_Player_History")
fixtures_df = pd.read_excel(file_path, sheet_name="Fixtures")

# -------------------------------
# STEP 2: BASIC CLEANING
# -------------------------------
df = df.fillna(0)

# Create player name if missing
if 'player_name' not in df.columns:
    if 'first_name' in df.columns and 'second_name' in df.columns:
        df['player_name'] = df['first_name'] + " " + df['second_name']
    else:
        df['player_name'] = df['player_id'].astype(str)

# -------------------------------
# STEP 3: SORT DATA
# -------------------------------
df = df.sort_values(['player_id', 'round'])

# -------------------------------
# STEP 4: CREATE TARGET (NEXT GW)
# -------------------------------
df['next_points'] = df.groupby('player_id')['total_points'].shift(-1)
df = df.dropna(subset=['next_points'])

# -------------------------------
# STEP 5: FEATURE ENGINEERING
# -------------------------------

# Recent form
df['form_last_3'] = df.groupby('player_id')['total_points'].transform(lambda x: x.rolling(3).mean())
df['form_last_5'] = df.groupby('player_id')['total_points'].transform(lambda x: x.rolling(5).mean())

# Home/Away
df['was_home'] = df['was_home'].fillna(0)

# Played last match
df['played_last_match'] = (df['minutes'] > 0).astype(int)

# Team strength
team_strength = df.groupby('team')['total_points'].mean().reset_index()
team_strength.columns = ['team', 'team_avg_points']
df = df.merge(team_strength, on='team', how='left')

# Fill NaNs
df[['form_last_3','form_last_5','team_avg_points']] = \
df[['form_last_3','form_last_5','team_avg_points']].fillna(0)

print("✅ Feature Engineering Done")

# Merge next_3_avg_difficulty from teams sheet
teams_df = pd.read_excel(file_path, sheet_name="Teams")
team_difficulty_map = dict(zip(teams_df['id'], teams_df['next_3_avg_difficulty']))
df['next_3_avg_difficulty'] = df['team'].map(team_difficulty_map)
df['next_3_avg_difficulty'] = df['next_3_avg_difficulty'].fillna(3.0)

# Position-specific scoring rates
df['goals_per_90'] = (df['goals_scored'] / (df['minutes'] / 90)).replace([float('inf')], 0).fillna(0)
df['assists_per_90'] = (df['assists'] / (df['minutes'] / 90)).replace([float('inf')], 0).fillna(0)
df['clean_sheet_rate'] = df.groupby('player_id')['clean_sheets'].transform(lambda x: x.rolling(5).mean()).fillna(0)
# -------------------------------
# STEP 6: Remove players with fewer than 20 minutes — too little data to predict reliably
# -------------------------------
df = df[df['minutes'] > MIN_MINUTES]

# -------------------------------
# STEP 7: DEFINE FEATURES
# -------------------------------
features = [
    'minutes', 'goals_scored', 'assists', 'clean_sheets',
    'goals_conceded', 'yellow_cards', 'red_cards',
    'now_cost', 'position_type', 'team',
    'form_last_3', 'form_last_5',
    'was_home',
    'team_avg_points',
    'played_last_match',
    'next_3_avg_difficulty',
    'goals_per_90',
    'assists_per_90',
    'clean_sheet_rate'
]

target = 'next_points'

# -------------------------------
# STEP 8: TIME-BASED SPLIT
# -------------------------------
split_gw = df['round'].quantile(SPLIT_PERCENTILE)

train_df = df[df['round'] <= split_gw]
test_df = df[df['round'] > split_gw]

X_train = train_df[features]
y_train = train_df[target]

X_test = test_df[features]
y_test = test_df[target]

print(f"Train size: {len(train_df)}, Test size: {len(test_df)}")

# -------------------------------
# STEP 9: TRAIN ALL MODELS
# -------------------------------
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

# --- Model 1: Random Forest (your existing model) ---
rf_model = RandomForestRegressor(
    n_estimators=N_ESTIMATORS,
    max_depth=MAX_DEPTH,
    min_samples_leaf=MIN_SAMPLES_LEAF,
    random_state=RANDOM_STATE,
    n_jobs=-1
)

# --- Model 2: XGBoost ---
xgb_model = XGBRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,      # learns slowly = more accurate
    subsample=0.8,           # uses 80% of data per tree = less overfitting
    colsample_bytree=0.8,    # uses 80% of features per tree
    random_state=RANDOM_STATE,
    verbosity=0              # stops it printing training logs
)

# --- Model 3: Linear Regression (baseline) ---
lr_model = LinearRegression()

# --- Model 4: Voting Ensemble ---
ensemble_model = VotingRegressor(estimators=[
    ('random_forest', rf_model),
    ('xgboost', xgb_model),
    ('linear_regression', lr_model)
])

# Train all 4
print("Training models...")

rf_model.fit(X_train, y_train)
print("✅ Random Forest trained")

xgb_model.fit(X_train, y_train)
print("✅ XGBoost trained")

lr_model.fit(X_train, y_train)
print("✅ Linear Regression trained")

ensemble_model.fit(X_train, y_train)
print("✅ Ensemble trained")

# -------------------------------
# STEP 10: COMPARE ALL MODELS
# -------------------------------
models = {
    'Random Forest': rf_model,
    'XGBoost': xgb_model,
    'Linear Regression': lr_model,
    'Ensemble': ensemble_model
}

print("\n📊 Model Comparison:")
print("-" * 35)

best_mae = float('inf')
best_model_name = ''
best_model = None

for name, m in models.items():
    preds = m.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    print(f"{name:<20} MAE: {round(mae, 3)}")

    if mae < best_mae:
        best_mae = mae
        best_model_name = name
        best_model = m

print("-" * 35)
print(f"🏆 Best Model: {best_model_name} (MAE: {round(best_mae, 2)})")

# -------------------------------
# STEP 11: SAVE VALIDATION
# using the best model
# -------------------------------
test_df = test_df.copy()
test_df['predicted_points'] = best_model.predict(X_test)
test_df['actual_points'] = test_df['next_points']
test_df['Player'] = test_df['player_name']

trust_df = test_df[[
    'Player', 'team', 'opponent_team',
    'actual_points', 'predicted_points'
]]
trust_df['error'] = abs(
    trust_df['actual_points'] - trust_df['predicted_points']
)
trust_df.to_excel(OUTPUT_VALIDATION, index=False)

# -------------------------------
# STEP 12: PREDICT WITH BEST MODEL
# -------------------------------
latest_df = df.sort_values('round').groupby('player_id').tail(1)
latest_df['predicted_points'] = best_model.predict(latest_df[features])

print(f"\n✅ Predictions made using: {best_model_name}")