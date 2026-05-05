import requests
import pandas as pd
from time import sleep

print("Starting FPL data fetch...")

# --- Step 1: Bootstrap data ---
url = "https://fantasy.premierleague.com/api/bootstrap-static/"
data = requests.get(url).json()

players_df = pd.DataFrame(data['elements'])
teams_df = pd.DataFrame(data['teams'])
gws_df = pd.DataFrame(data['events'])

print("Players:", players_df.shape)

# --- Step 2: Player info ---
players_info = players_df[['id','first_name','second_name','team','element_type','now_cost']].copy()
players_info.rename(columns={
    'id':'player_id',
    'element_type':'position_type'
}, inplace=True)

# --- Step 3: Fixtures ---
fixtures = requests.get("https://fantasy.premierleague.com/api/fixtures/").json()
fixtures_df = pd.DataFrame(fixtures)

# --- Step 4: Fetch player histories ---
all_histories = []

for i, pid in enumerate(players_info['player_id'], 1):
    print(f"[{i}/{len(players_info)}] Fetching player data...")

    url = f"https://fantasy.premierleague.com/api/element-summary/{pid}/"
    player_data = requests.get(url).json()

    history = player_data['history']

    if history:
        df = pd.DataFrame(history)
        df['player_id'] = pid
        all_histories.append(df)

    sleep(0.2)

# --- Combine ---
player_history_df = pd.concat(all_histories, ignore_index=True)

# --- Merge ---
merged_history_df = player_history_df.merge(players_info, on='player_id', how='left')
# After merging histories, add this before saving Excel:

# Convert position_type number to label
position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
merged_history_df['position_label'] = merged_history_df['position_type'].map(position_map)

# Next 3 GW difficulty per team
future_fixtures = fixtures_df[fixtures_df['finished'] == False].sort_values('event')

def get_next_n_difficulty(team_id, n=3):
    home = future_fixtures[future_fixtures['team_h'] == team_id][['team_h_difficulty']].head(n)
    away = future_fixtures[future_fixtures['team_a'] == team_id][['team_a_difficulty']].head(n)
    home.columns = ['difficulty']
    away.columns = ['difficulty']
    combined = pd.concat([home, away]).head(n)
    return combined['difficulty'].mean() if len(combined) > 0 else 3.0

teams_df['next_3_avg_difficulty'] = teams_df['id'].apply(get_next_n_difficulty)

# Save this into Excel as new sheet
# Add teams_df with next_3_avg_difficulty to your ExcelWriter

# --- Add name ---
merged_history_df['player_name'] = (
    merged_history_df['first_name'] + " " + merged_history_df['second_name']
)

print("Merged data shape:", merged_history_df.shape)

# --- Save Excel ---
with pd.ExcelWriter("fpl_data_all_players_merged.xlsx", engine="openpyxl") as writer:
    players_df.to_excel(writer, sheet_name="Players", index=False)
    teams_df.to_excel(writer, sheet_name="Teams", index=False)
    #teams_df.to_excel(writer, sheet_name="Teams", index=False)  # already exists, now has new column
    fixtures_df.to_excel(writer, sheet_name="Fixtures", index=False)
    merged_history_df.to_excel(writer, sheet_name="Merged_Player_History", index=False)

print("✅ Data saved: fpl_data_all_players_merged.xlsx")