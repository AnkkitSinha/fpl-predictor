# ⚽ FPL Intelligence

> A machine learning powered Fantasy Premier League prediction and squad management tool. Built with Python, scikit-learn, XGBoost and Streamlit.

---

## What is this?

FPL Intelligence is a data-driven tool for Fantasy Premier League (FPL) managers. Every week, FPL managers make decisions about which players to pick, who to captain, and who to transfer in or out. Most of these decisions are made on gut feeling, basic form tables, or manual research.

This tool automates that entire process. It pulls live data from the official FPL API, engineers predictive features from that data, trains multiple machine learning models to predict how many points each player will score in the next gameweek, and then presents those predictions in an interactive dashboard where managers can explore the data, analyse their own squad, and get personalised recommendations.

The goal is to give any FPL manager access to the kind of data analysis that would otherwise require hours of manual research — in a few seconds.

---

## How it works

The project runs as a three-stage pipeline:

```
Stage 1             Stage 2              Stage 3
─────────────       ──────────────       ──────────────────
data_fetch.py  →    model.py       →     app.py
                                         
Pulls data          Engineers            Displays predictions
from FPL API        features,            in interactive
and saves to        trains models,       Streamlit dashboard
Excel               saves predictions
```

You run Stage 1 and Stage 2 manually (or via the refresh button in the app). Stage 3 runs continuously as the dashboard.

---

## Where the data comes from

All data is pulled from the **official Fantasy Premier League API**, which is publicly available and free to use. No scraping — this is a legitimate documented API.

The following endpoints are used:

### 1. Bootstrap Static
```
https://fantasy.premierleague.com/api/bootstrap-static/
```
This is the main endpoint. It returns a large JSON payload containing:
- **All players** — every player currently in the FPL database (700+ players), including their name, team, position, current price, and season-level stats
- **All teams** — all 20 Premier League teams with IDs and names
- **All gameweeks** — the full season schedule with gameweek numbers and deadlines

### 2. Fixtures
```
https://fantasy.premierleague.com/api/fixtures/
```
Returns every match in the season — past and future — including:
- Home and away team IDs
- Whether the match has been played (finished: true/false)
- Fixture Difficulty Rating (FDR) for each team, from 1 (easiest) to 5 (hardest)
- Gameweek number (event)

### 3. Player History (one request per player)
```
https://fantasy.premierleague.com/api/element-summary/{player_id}/
```
This is the most detailed endpoint. For every single player, it returns their gameweek-by-gameweek history for the entire current season. Each row in the history contains:

Since there are 700+ players, this stage makes 700+ individual API requests. A 0.2 second delay is added between each request to avoid hitting rate limits. This stage takes approximately 5-10 minutes to complete.

### Data Volume
A typical full season fetch produces roughly:
- ~700 players
- ~30 gameweeks of history per player
- ~21,000 rows of player-gameweek data
- All saved into a single Excel file with multiple sheets

---

## What we do with the data

### Step 1 — Cleaning
- Fill missing values with 0 (common for stats like goals/assists for players who didn't play)
- Remove players who played fewer than 20 minutes in a gameweek — these rows add noise without useful signal since substitute appearances distort per-match stats

### Step 2 — Feature Engineering
This is the most important step. Raw data alone is not predictive — we need to derive meaningful signals from it. The following features are engineered:

**Form features**
- `form_last_3` — rolling average of points scored over the last 3 gameweeks per player. Captures short-term momentum
- `form_last_5` — rolling average of points over the last 5 gameweeks. Captures slightly longer trends
- `played_last_match` — binary flag (1/0) for whether the player played last gameweek. Players who didn't play have much lower probability of scoring well

**Performance rate features**
- `goals_per_90` — goals scored per 90 minutes played. Normalises goal scoring for players who rotate or come off the bench
- `assists_per_90` — assists per 90 minutes played. Same normalisation logic
- `clean_sheet_rate` — rolling 5-game average of clean sheets. Most relevant for goalkeepers and defenders

**Context features**
- `team_avg_points` — the average points per gameweek for the player's team. Acts as a proxy for overall team quality
- `was_home` — home teams historically score more FPL points on average
- `next_3_avg_difficulty` — average Fixture Difficulty Rating for the next 3 gameweeks. A player with 3 easy games coming up is more likely to score well than a player facing 3 top-six sides

### Step 3 — Target Variable
The target we're trying to predict is `next_points` — the total points a player will score in their **next** gameweek. This is created by shifting the `total_points` column backwards by one row within each player group. In other words, for any given gameweek, we're trying to predict the row that comes after it.

### Step 4 — Train/Test Split
Rather than a random split, we use a **time-based split** — the first 80% of gameweeks are used for training, and the most recent 20% are used for testing. This is critical for sports data. A random split would allow the model to "see the future" during training, making it look more accurate than it really is. A time-based split mimics real-world usage — you can only train on what you knew at the time.

### Step 5 — Predictions on Latest Data
Once trained, the model predicts on the **most recent gameweek data per player** — this is the actual next-gameweek prediction that the dashboard displays.

---

## Machine learning models

Four models are trained and compared every time `model.py` is run. The one with the lowest Mean Absolute Error (MAE) on the test set is automatically selected for the final predictions.

### Model 1 — Random Forest
An ensemble of decision trees where each tree is trained on a random subset of the data and features. Trees are built independently and their predictions are averaged. Good baseline for this kind of mixed numeric and categorical data.

### Model 2 — XGBoost (Gradient Boosted Trees)
Similar to Random Forest but trees are built sequentially — each new tree focuses on correcting the errors made by the previous one. Generally outperforms Random Forest on structured/tabular data, which is why it is the most commonly used model in data science competitions. Usually achieves the best individual MAE in this pipeline.

### Model 3 — Linear Regression
A simple model that finds a linear relationship between each feature and the target. Included as a baseline sanity check. If a complex model like XGBoost is only marginally better than Linear Regression, it suggests the features need improving rather than the model.

### Model 4 — Voting Ensemble
Combines all three models by averaging their predictions. Even if XGBoost is individually the best, the ensemble tends to be more stable because when one model gets a prediction wrong, the others can compensate. Generally produces the most reliable real-world results.

### Evaluation Metric
Models are evaluated using **Mean Absolute Error (MAE)** — the average number of points the prediction is off by. An MAE of 2.1 means on average the model predicts within 2.1 points of the actual score. For context, most FPL players score between 1 and 12 points per gameweek.
---

## Features

### 🏆 Predictions Tab
- Top 20 predicted players for the upcoming gameweek
- Captain and vice-captain suggestion with reasoning
- KPI summary cards (avg predicted points, top player, best value, player count)
- Player selection scatter chart divided into four quadrants: Must Buy, Differential, Sell Candidate, Avoid
- Horizontal bar chart of top 20 predicted points
- Average predicted points by position breakdown
- Fixture difficulty colour coding in all tables (green = easy, yellow = medium, red = hard)
- Download filtered data as CSV

### 👤 My Squad Tab
- Select your 15 players from a searchable dropdown
- Enter your remaining transfer budget
- See your personal captain and vice captain recommendation based only on players you own
- Squad predicted points bar chart broken down by position
- Personalised transfer recommendations — identifies your 3 weakest performing players and suggests the best affordable same-position replacement from the rest of the player pool

### 📅 Fixture Planner Tab
- Colour coded 5-gameweek fixture difficulty grid for all 20 Premier League teams
- Shows opponent name, home/away, and FDR rating for each upcoming gameweek
- Best fixture run chart — ranks teams by their average difficulty over the next 5 gameweeks
- Useful for planning transfers and identifying which team's players to target

### 🎯 Differentials Tab
- Players with above-average predicted points but below-average recent form
- These are players the model thinks are about to bounce back — likely to have low ownership
- Ideal for finding the edge over other FPL managers

### 💰 Value Picks Tab
- Ranks players by value-for-money score (predicted points divided by price)
- Price vs predicted points scatter plot
- Essential for building a balanced squad within the budget

### 📊 Model Accuracy Tab
- Predicted vs actual points scatter plot with perfect prediction reference line
- Error distribution histogram
- "Predictions within 2 points" percentage metric
- Full validation table with per-player actual vs predicted results
- Searchable by player name

---

