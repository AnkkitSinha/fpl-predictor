import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess
import os
import sys
from datetime import datetime

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="FPL Intelligence",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# CUSTOM CSS
# ==============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
    }

    .main {
        background-color: #0d1117;
        color: #e6edf3;
    }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1c2333, #161b27);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #58a6ff;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Captain Card */
    .captain-card {
        background: linear-gradient(135deg, #0d4429, #0a2d1c);
        border: 1px solid #238636;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 10px;
    }
    .vc-card {
        background: linear-gradient(135deg, #0c2d6b, #071d4a);
        border: 1px solid #1f6feb;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 10px;
    }
    .card-name {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
    }
    .card-detail {
        font-size: 0.9rem;
        color: #8b949e;
        margin-top: 4px;
    }
    .card-badge {
        display: inline-block;
        background: #238636;
        color: white;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .vc-badge {
        display: inline-block;
        background: #1f6feb;
        color: white;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 8px;
    }

    /* Squad player card */
    .player-card {
        background: #1c2333;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Section headers */
    .section-header {
        font-family: 'Syne', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #e6edf3;
        border-left: 3px solid #58a6ff;
        padding-left: 12px;
        margin: 24px 0 16px 0;
    }

    /* Fixture difficulty pills */
    .diff-1, .diff-2 { background: #1a7f37; color: white; border-radius: 6px; padding: 4px 10px; font-size: 0.8rem; font-weight: 600; }
    .diff-3 { background: #9e6a03; color: white; border-radius: 6px; padding: 4px 10px; font-size: 0.8rem; font-weight: 600; }
    .diff-4, .diff-5 { background: #b62324; color: white; border-radius: 6px; padding: 4px 10px; font-size: 0.8rem; font-weight: 600; }

    /* Streamlit overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #161b27;
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #8b949e;
        font-family: 'Syne', sans-serif;
        font-weight: 600;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: #1c2333 !important;
        color: #58a6ff !important;
    }
    .stMetric {
        background: #1c2333;
        border-radius: 10px;
        padding: 16px !important;
        border: 1px solid #30363d;
    }
    div[data-testid="metric-container"] {
        background: #1c2333;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
    }
    .stSidebar {
        background: #161b27;
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    .refresh-box {
        background: #1c2333;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #238636, #1a7f37);
        color: white;
        border: none;
        border-radius: 8px;
        font-family: 'Syne', sans-serif;
        font-weight: 600;
        padding: 8px 20px;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2ea043, #238636);
        transform: translateY(-1px);
    }
    .transfer-in {
        background: linear-gradient(135deg, #0d4429, #0a2d1c);
        border: 1px solid #238636;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 8px;
    }
    .transfer-out {
        background: linear-gradient(135deg, #3d1f1f, #2d1515);
        border: 1px solid #b62324;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 8px;
    }
    .warning-box {
        background: #272115;
        border: 1px solid #9e6a03;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        color: #e3b341;
    }
</style>
""", unsafe_allow_html=True)


# ==============================
# DATA LOADING WITH ERROR HANDLING
# ==============================
@st.cache_data(ttl=3600)
def load_data():
    errors = []
    df = pd.DataFrame()
    val_df = pd.DataFrame()
    fixtures_df = pd.DataFrame()
    teams_df = pd.DataFrame()

    try:
        df = pd.read_excel("fpl_predictions_trustworthy.xlsx")
        position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        if 'position_type' in df.columns:
            df['Position'] = df['position_type'].map(position_map)
        else:
            df['Position'] = 'Unknown'
    except Exception as e:
        errors.append(f"Predictions file: {e}")

    try:
        val_df = pd.read_excel("model_validation.xlsx")
        val_df['order'] = range(len(val_df))
        val_df = val_df.sort_values(['Player', 'order'])
        val_df = val_df.groupby('Player').tail(1)
        val_df = val_df.rename(columns={
            'actual_points': 'Actual Points',
            'predicted_points': 'Predicted Points'
        })
    except Exception as e:
        errors.append(f"Validation file: {e}")

    try:
        fixtures_df = pd.read_excel("fpl_data_all_players_merged.xlsx", sheet_name="Fixtures")
        teams_df = pd.read_excel("fpl_data_all_players_merged.xlsx", sheet_name="Teams")
    except Exception as e:
        errors.append(f"Fixtures/Teams data: {e}")

    return df, val_df, fixtures_df, teams_df, errors


def refresh_data():
    """Run data fetch and model scripts"""
    results = []
    scripts = ['data_fetch.py', 'model.py']
    for script in scripts:
        if os.path.exists(script):
            try:
                result = subprocess.run(
                    [sys.executable, script],
                    capture_output=True, text=True, timeout=300
                )
                if result.returncode == 0:
                    results.append(f"✅ {script} completed")
                else:
                    results.append(f"❌ {script} failed: {result.stderr[:200]}")
            except subprocess.TimeoutExpired:
                results.append(f"⏱️ {script} timed out (>5 mins)")
            except Exception as e:
                results.append(f"❌ {script} error: {e}")
        else:
            results.append(f"⚠️ {script} not found in current directory")
    return results


def colour_difficulty(val):
    try:
        val = float(val)
        if val <= 2:
            return 'background-color: #1a7f37; color: white'
        elif val == 3:
            return 'background-color: #9e6a03; color: white'
        else:
            return 'background-color: #b62324; color: white'
    except:
        return ''


def build_fixture_grid(fixtures_df, teams_df, n_gws=5):
    """Build next N gameweek fixture difficulty grid per team"""
    if fixtures_df.empty or teams_df.empty:
        return pd.DataFrame()

    team_map = dict(zip(teams_df['id'], teams_df['name']))
    future = fixtures_df[fixtures_df['finished'] == False].copy()
    future = future.sort_values('event')

    rows = []
    for team_id, team_name in team_map.items():
        home = future[future['team_h'] == team_id][['event', 'team_a', 'team_h_difficulty']].copy()
        home.columns = ['GW', 'opponent', 'difficulty']
        home['venue'] = 'H'

        away = future[future['team_a'] == team_id][['event', 'team_h', 'team_a_difficulty']].copy()
        away.columns = ['GW', 'opponent', 'difficulty']
        away['venue'] = 'A'

        combined = pd.concat([home, away]).sort_values('GW').head(n_gws)
        combined['opponent'] = combined['opponent'].map(team_map)
        combined['Team'] = team_name

        row = {'Team': team_name}
        for i, (_, fix) in enumerate(combined.iterrows()):
            gw_label = f"GW{int(fix['GW'])}"
            row[gw_label] = f"{fix['opponent']} ({fix['venue']}) [{int(fix['difficulty'])}]"
            row[f"{gw_label}_diff"] = int(fix['difficulty'])

        rows.append(row)

    return pd.DataFrame(rows)


# ==============================
# LOAD DATA
# ==============================
df, val_df, fixtures_df, teams_df, load_errors = load_data()

# ==============================
# HEADER
# ==============================
st.markdown("""
<div style="padding: 10px 0 20px 0;">
    <h1 style="color: #58a6ff; margin: 0; font-size: 2.5rem;">⚽ FPL Intelligence</h1>
    <p style="color: #8b949e; margin: 4px 0 0 0; font-size: 1rem;">
        AI-powered Fantasy Premier League predictions & squad analysis
    </p>
</div>
""", unsafe_allow_html=True)

# Show load errors if any
if load_errors:
    st.markdown('<div class="warning-box">⚠️ <strong>Some data could not be loaded:</strong><br>' +
                '<br>'.join(load_errors) +
                '<br><br>Run <code>data_fetch.py</code> and <code>model.py</code> first, or use the refresh button in the sidebar.</div>',
                unsafe_allow_html=True)

# ==============================
# SIDEBAR
# ==============================
st.sidebar.markdown("## ⚙️ Controls")

# --- Data Refresh ---
st.sidebar.markdown('<div class="refresh-box">', unsafe_allow_html=True)
st.sidebar.markdown("**🔄 Data Refresh**")

last_modified = ""
try:
    ts = os.path.getmtime("fpl_predictions_trustworthy.xlsx")
    last_modified = datetime.fromtimestamp(ts).strftime("%d %b %Y, %H:%M")
    st.sidebar.markdown(f"<small style='color:#8b949e'>Last updated: {last_modified}</small>", unsafe_allow_html=True)
except:
    st.sidebar.markdown("<small style='color:#8b949e'>Last updated: unknown</small>", unsafe_allow_html=True)

if st.sidebar.button("🔄 Refresh Data Now"):
    with st.spinner("Running data fetch and model... this takes 5-10 mins"):
        results = refresh_data()
    for r in results:
        st.sidebar.write(r)
    if all("✅" in r for r in results):
        st.cache_data.clear()
        st.rerun()

st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🔍 Filters")

# Filters (only show if data loaded)
if not df.empty:
    team_filter = st.sidebar.multiselect(
        "Select Team",
        options=sorted(df['Team'].dropna().unique()),
        default=sorted(df['Team'].dropna().unique())
    )

    price_filter = st.sidebar.slider(
        "Max Price (×10 = £m)",
        min_value=int(df['now_cost'].min()),
        max_value=int(df['now_cost'].max()),
        value=int(df['now_cost'].max())
    )

    position_filter = st.sidebar.multiselect(
        "Select Position",
        options=['GK', 'DEF', 'MID', 'FWD'],
        default=['GK', 'DEF', 'MID', 'FWD']
    )

    player_search = st.sidebar.text_input("🔎 Search Player", key="player_search_input")

    # Apply filters
    filtered_df = df[
        (df['Team'].isin(team_filter)) &
        (df['now_cost'] <= price_filter) &
        (df['Position'].isin(position_filter))
    ].copy()

    filtered_df['decision_score'] = (
        filtered_df['Predicted Points'] * 0.6 +
        filtered_df['last_5_avg'] * 0.3 +
        filtered_df['last_3_avg'] * 0.1
    )
else:
    filtered_df = pd.DataFrame()
    player_search = ""

st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#8b949e'>FPL Intelligence v2.0<br>Built with ❤️ using Python & Streamlit</small>", unsafe_allow_html=True)

# ==============================
# STOP IF NO DATA
# ==============================
if filtered_df.empty:
    st.error("No data available. Please run data_fetch.py and model.py first, then click Refresh Data.")
    st.stop()

# ==============================
# CAPTAIN + VC LOGIC
# ==============================
captain_df = filtered_df.copy()
captain_df['captain_score'] = (
    captain_df['Predicted Points'] * 0.7 +
    captain_df['last_3_avg'] * 0.3
)
top_captain = captain_df.sort_values('captain_score', ascending=False).iloc[0]
vice_captain = captain_df.sort_values('captain_score', ascending=False).iloc[1]

# ==============================
# TABS
# ==============================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏆 Predictions",
    "👤 My Squad",
    "📅 Fixture Planner",
    "🎯 Differentials",
    "💰 Value Picks",
    "📊 Model Accuracy"
])


# ==============================
# TAB 1 — PREDICTIONS
# ==============================
with tab1:

    # Captain Cards
    st.markdown('<div class="section-header">🎖️ Captain Suggestion This Week</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="captain-card">
            <div class="card-badge">⭐ CAPTAIN</div>
            <div class="card-name">{top_captain['Player']}</div>
            <div class="card-detail">🏟️ {top_captain['Team']} &nbsp;|&nbsp; {top_captain.get('Position','')}</div>
            <div class="card-detail">📈 Predicted: <strong style="color:#58a6ff">{round(top_captain['Predicted Points'],1)} pts</strong></div>
            <div class="card-detail">📊 Last 3 avg: {round(top_captain['last_3_avg'],1)} &nbsp;|&nbsp; Last 5 avg: {round(top_captain['last_5_avg'],1)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="vc-card">
            <div class="vc-badge">🔵 VICE CAPTAIN</div>
            <div class="card-name">{vice_captain['Player']}</div>
            <div class="card-detail">🏟️ {vice_captain['Team']} &nbsp;|&nbsp; {vice_captain.get('Position','')}</div>
            <div class="card-detail">📈 Predicted: <strong style="color:#58a6ff">{round(vice_captain['Predicted Points'],1)} pts</strong></div>
            <div class="card-detail">📊 Last 3 avg: {round(vice_captain['last_3_avg'],1)} &nbsp;|&nbsp; Last 5 avg: {round(vice_captain['last_5_avg'],1)}</div>
        </div>
        """, unsafe_allow_html=True)

    # KPI Cards
    st.markdown('<div class="section-header">📊 This Week at a Glance</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Avg Predicted Points", round(filtered_df['Predicted Points'].mean(), 1))
    col2.metric("Top Predicted Player",
                filtered_df.sort_values('Predicted Points', ascending=False).iloc[0]['Player'].split()[-1])
    col3.metric("Best Value Pick",
                filtered_df.sort_values('value_for_money', ascending=False).iloc[0]['Player'].split()[-1])
    col4.metric("Players Analysed", len(filtered_df))

    # Top 20 Table
    st.markdown('<div class="section-header">🔥 Top 20 Players</div>', unsafe_allow_html=True)
    top_players = filtered_df.sort_values('Predicted Points', ascending=False).head(20)

    display_cols = ['Player', 'Position', 'Team', 'Predicted Points',
                    'last_3_avg', 'last_5_avg', 'Fixture Difficulty', 'now_cost']
    top_display = top_players[[c for c in display_cols if c in top_players.columns]].copy()
    top_display['now_cost'] = (top_display['now_cost'] / 10).round(1).astype(str) + "m"

    if 'Fixture Difficulty' in top_display.columns:
        st.dataframe(
            top_display.style.applymap(colour_difficulty, subset=['Fixture Difficulty']),
            use_container_width=True, hide_index=True
        )
    else:
        st.dataframe(top_display, use_container_width=True, hide_index=True)

    # Bar Chart
    st.markdown('<div class="section-header">📊 Predicted Points — Top 20</div>', unsafe_allow_html=True)
    fig_bar = px.bar(
        top_players.sort_values('Predicted Points'),
        x='Predicted Points',
        y='Player',
        orientation='h',
        color='Predicted Points',
        color_continuous_scale='Blues',
        template='plotly_dark'
    )
    fig_bar.update_layout(
        plot_bgcolor='#161b27', paper_bgcolor='#161b27',
        font=dict(color='#e6edf3'),
        showlegend=False, height=500,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Scatter Plot
    st.markdown('<div class="section-header">📊 Player Selection Chart</div>', unsafe_allow_html=True)
    st.caption("Top-right = Must Buy | Top-left = Differential | Bottom-right = Sell | Bottom-left = Avoid")

    avg_pred = filtered_df['Predicted Points'].mean()
    avg_form = filtered_df['last_5_avg'].mean()

    fig_scatter = px.scatter(
        filtered_df,
        x='last_5_avg',
        y='Predicted Points',
        hover_data=['Player', 'Team', 'last_3_avg', 'Fixture Difficulty'],
        size='now_cost',
        color='Predicted Points',
        color_continuous_scale='Blues',
        template='plotly_dark'
    )
    fig_scatter.add_hline(y=avg_pred, line_dash="dash", line_color="#58a6ff", opacity=0.5)
    fig_scatter.add_vline(x=avg_form, line_dash="dash", line_color="#58a6ff", opacity=0.5)

    fig_scatter.add_annotation(x=avg_form * 0.2, y=filtered_df['Predicted Points'].max() * 0.95,
        text="🎯 Differential", showarrow=False, font=dict(size=11, color="#e3b341"))
    fig_scatter.add_annotation(x=filtered_df['last_5_avg'].max() * 0.8, y=filtered_df['Predicted Points'].max() * 0.95,
        text="✅ Must Buy", showarrow=False, font=dict(size=11, color="#3fb950"))
    fig_scatter.add_annotation(x=avg_form * 0.2, y=avg_pred * 0.3,
        text="❌ Avoid", showarrow=False, font=dict(size=11, color="#f85149"))
    fig_scatter.add_annotation(x=filtered_df['last_5_avg'].max() * 0.8, y=avg_pred * 0.3,
        text="⚠️ Sell", showarrow=False, font=dict(size=11, color="#bc8cff"))

    fig_scatter.update_layout(
        plot_bgcolor='#161b27', paper_bgcolor='#161b27',
        font=dict(color='#e6edf3'), height=500,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Position breakdown
    st.markdown('<div class="section-header">📊 Average Predicted Points by Position</div>', unsafe_allow_html=True)
    pos_summary = filtered_df.groupby('Position')['Predicted Points'].mean().reset_index()
    fig_pos = px.bar(pos_summary, x='Position', y='Predicted Points',
                     color='Position', template='plotly_dark',
                     color_discrete_map={'GK':'#58a6ff','DEF':'#3fb950','MID':'#e3b341','FWD':'#f85149'})
    fig_pos.update_layout(plot_bgcolor='#161b27', paper_bgcolor='#161b27',
                          font=dict(color='#e6edf3'), showlegend=False,
                          margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_pos, use_container_width=True)

    # Download
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False),
        file_name='fpl_filtered.csv',
        mime='text/csv'
    )


# ==============================
# TAB 2 — MY SQUAD
# ==============================
with tab2:

    st.markdown('<div class="section-header">👤 My Squad</div>', unsafe_allow_html=True)
    st.write("Select your 15 players to get personalised captain, transfer, and chip recommendations.")

    all_players = sorted(df['Player'].dropna().unique().tolist())

    # Initialise session state for squad
    if 'my_squad' not in st.session_state:
        st.session_state.my_squad = []

    # Squad input
    col_input, col_budget = st.columns([3, 1])

    with col_input:
        selected_squad = st.multiselect(
            "Select your 15 players",
            options=all_players,
            default=st.session_state.my_squad,
            max_selections=15,
            key="squad_selector"
        )
        st.session_state.my_squad = selected_squad

    with col_budget:
        budget_remaining = st.number_input(
            "Budget remaining (£m)",
            min_value=0.0,
            max_value=20.0,
            value=0.0,
            step=0.1
        )

    if len(selected_squad) == 0:
        st.markdown('<div class="warning-box">👆 Select your 15 players above to see personalised recommendations.</div>',
                    unsafe_allow_html=True)

    elif len(selected_squad) < 15:
        st.info(f"Select {15 - len(selected_squad)} more player(s) to complete your squad.")
        # Still show partial squad
        squad_df = df[df['Player'].isin(selected_squad)].copy()

        if not squad_df.empty:
            st.markdown('<div class="section-header">Your Current Players</div>', unsafe_allow_html=True)
            sq_display = squad_df[['Player','Position','Team','Predicted Points','last_3_avg','now_cost']].copy()
            sq_display['now_cost'] = (sq_display['now_cost'] / 10).round(1).astype(str) + "m"
            sq_display = sq_display.sort_values('Position')
            st.dataframe(sq_display, use_container_width=True, hide_index=True)

    else:
        squad_df = df[df['Player'].isin(selected_squad)].copy()

        # --- Squad Summary ---
        st.markdown('<div class="section-header">📋 Squad Summary</div>', unsafe_allow_html=True)

        sq_col1, sq_col2, sq_col3, sq_col4 = st.columns(4)
        sq_col1.metric("Squad Avg Predicted Pts", round(squad_df['Predicted Points'].mean(), 1))
        sq_col2.metric("Best Captain Option", squad_df.sort_values('Predicted Points', ascending=False).iloc[0]['Player'].split()[-1])
        sq_col3.metric("Squad Value",
                       f"£{round(squad_df['now_cost'].sum() / 10, 1)}m")
        sq_col4.metric("Players in Form",
                       len(squad_df[squad_df['last_3_avg'] > squad_df['last_3_avg'].mean()]))

        # --- Squad Table ---
        sq_display = squad_df[[c for c in ['Player','Position','Team','Predicted Points',
                                            'last_3_avg','last_5_avg','Fixture Difficulty','now_cost']
                                if c in squad_df.columns]].copy()
        sq_display['now_cost'] = (sq_display['now_cost'] / 10).round(1).astype(str) + "m"
        sq_display = sq_display.sort_values('Predicted Points', ascending=False)

        if 'Fixture Difficulty' in sq_display.columns:
            st.dataframe(
                sq_display.style.applymap(colour_difficulty, subset=['Fixture Difficulty']),
                use_container_width=True, hide_index=True
            )
        else:
            st.dataframe(sq_display, use_container_width=True, hide_index=True)

        # --- Captain Recommendation from your squad ---
        st.markdown('<div class="section-header">🎖️ Captain Pick from Your Squad</div>', unsafe_allow_html=True)

        squad_cap = squad_df.copy()
        squad_cap['captain_score'] = squad_cap['Predicted Points'] * 0.7 + squad_cap['last_3_avg'] * 0.3
        sq_captain = squad_cap.sort_values('captain_score', ascending=False).iloc[0]
        sq_vc = squad_cap.sort_values('captain_score', ascending=False).iloc[1]

        cap_col1, cap_col2 = st.columns(2)
        with cap_col1:
            st.markdown(f"""
            <div class="captain-card">
                <div class="card-badge">⭐ CAPTAIN</div>
                <div class="card-name">{sq_captain['Player']}</div>
                <div class="card-detail">🏟️ {sq_captain['Team']}</div>
                <div class="card-detail">📈 Predicted: <strong style="color:#58a6ff">{round(sq_captain['Predicted Points'],1)} pts</strong></div>
                <div class="card-detail">📊 Last 3: {round(sq_captain['last_3_avg'],1)} | Last 5: {round(sq_captain['last_5_avg'],1)}</div>
            </div>
            """, unsafe_allow_html=True)
        with cap_col2:
            st.markdown(f"""
            <div class="vc-card">
                <div class="vc-badge">🔵 VICE CAPTAIN</div>
                <div class="card-name">{sq_vc['Player']}</div>
                <div class="card-detail">🏟️ {sq_vc['Team']}</div>
                <div class="card-detail">📈 Predicted: <strong style="color:#58a6ff">{round(sq_vc['Predicted Points'],1)} pts</strong></div>
                <div class="card-detail">📊 Last 3: {round(sq_vc['last_3_avg'],1)} | Last 5: {round(sq_vc['last_5_avg'],1)}</div>
            </div>
            """, unsafe_allow_html=True)

        # --- Transfer Recommendations ---
        st.markdown('<div class="section-header">🔄 Transfer Recommendations</div>', unsafe_allow_html=True)
        st.caption("Players to consider selling (your worst performers) and their best replacements not in your squad.")

        # Worst performers in your squad
        worst = squad_df.sort_values('Predicted Points').head(3)

        # Best players NOT in your squad
        not_in_squad = df[~df['Player'].isin(selected_squad)].copy()

        for _, player_out in worst.iterrows():
            position = player_out.get('Position', '')
            price_out = player_out['now_cost']
            max_price = price_out + (budget_remaining * 10)

            # Find best replacement: same position, affordable, not in squad
            replacements = not_in_squad[
                (not_in_squad['Position'] == position) &
                (not_in_squad['now_cost'] <= max_price)
            ].sort_values('Predicted Points', ascending=False).head(1)

            col_out, col_arrow, col_in = st.columns([5, 1, 5])

            with col_out:
                st.markdown(f"""
                <div class="transfer-out">
                    <strong style="color:#f85149">❌ Transfer Out</strong><br>
                    <strong>{player_out['Player']}</strong> ({position})<br>
                    <small style="color:#8b949e">Predicted: {round(player_out['Predicted Points'],1)} pts &nbsp;|&nbsp;
                    Form: {round(player_out['last_3_avg'],1)} &nbsp;|&nbsp;
                    £{round(price_out/10,1)}m</small>
                </div>
                """, unsafe_allow_html=True)

            with col_arrow:
                st.markdown("<br><br><h2 style='text-align:center'>→</h2>", unsafe_allow_html=True)

            with col_in:
                if not replacements.empty:
                    rep = replacements.iloc[0]
                    price_diff = rep['now_cost'] - price_out
                    diff_str = f"+£{abs(price_diff/10):.1f}m" if price_diff > 0 else f"-£{abs(price_diff/10):.1f}m"
                    st.markdown(f"""
                    <div class="transfer-in">
                        <strong style="color:#3fb950">✅ Transfer In</strong><br>
                        <strong>{rep['Player']}</strong> ({position})<br>
                        <small style="color:#8b949e">Predicted: {round(rep['Predicted Points'],1)} pts &nbsp;|&nbsp;
                        Form: {round(rep['last_3_avg'],1)} &nbsp;|&nbsp;
                        £{round(rep['now_cost']/10,1)}m ({diff_str})</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="transfer-in">
                        <strong style="color:#3fb950">✅ Transfer In</strong><br>
                        No affordable replacement found.<br>
                        <small style="color:#8b949e">Try increasing budget remaining.</small>
                    </div>
                    """, unsafe_allow_html=True)

        # --- Squad points bar chart ---
        st.markdown('<div class="section-header">📊 Your Squad Predicted Points</div>', unsafe_allow_html=True)
        fig_squad = px.bar(
            squad_df.sort_values('Predicted Points'),
            x='Predicted Points', y='Player',
            orientation='h', color='Position',
            template='plotly_dark',
            color_discrete_map={'GK':'#58a6ff','DEF':'#3fb950','MID':'#e3b341','FWD':'#f85149'}
        )
        fig_squad.update_layout(
            plot_bgcolor='#161b27', paper_bgcolor='#161b27',
            font=dict(color='#e6edf3'), height=450,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_squad, use_container_width=True)


# ==============================
# TAB 3 — FIXTURE PLANNER
# ==============================
with tab3:

    st.markdown('<div class="section-header">📅 5-Gameweek Fixture Planner</div>', unsafe_allow_html=True)
    st.write("Colour coded fixture difficulty for every team over the next 5 gameweeks. Green = easy, Red = hard.")

    if fixtures_df.empty or teams_df.empty:
        st.warning("Fixture data not available. Make sure fpl_data_all_players_merged.xlsx exists and has Fixtures and Teams sheets.")
    else:
        fixture_grid = build_fixture_grid(fixtures_df, teams_df, n_gws=5)

        if fixture_grid.empty:
            st.warning("No upcoming fixtures found.")
        else:
            # Get GW columns
            gw_cols = [c for c in fixture_grid.columns if c.startswith('GW') and not c.endswith('_diff')]
            diff_cols = [c for c in fixture_grid.columns if c.endswith('_diff')]

            display_grid = fixture_grid[['Team'] + gw_cols].copy()

            # Style function for fixture grid
            def style_fixture_grid(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                for gw_col in gw_cols:
                    diff_col = gw_col + '_diff'
                    if diff_col in fixture_grid.columns:
                        for idx in df.index:
                            try:
                                diff = fixture_grid.loc[idx, diff_col]
                                if diff <= 2:
                                    styles.loc[idx, gw_col] = 'background-color: #1a7f37; color: white; font-weight: 600'
                                elif diff == 3:
                                    styles.loc[idx, gw_col] = 'background-color: #9e6a03; color: white; font-weight: 600'
                                else:
                                    styles.loc[idx, gw_col] = 'background-color: #b62324; color: white; font-weight: 600'
                            except:
                                pass
                return styles

            st.dataframe(
                display_grid.style.apply(style_fixture_grid, axis=None),
                use_container_width=True,
                hide_index=True,
                height=600
            )

            st.markdown("""
            <div style="display:flex; gap:16px; margin-top:12px;">
                <span style="background:#1a7f37; color:white; padding:4px 12px; border-radius:6px; font-size:0.85rem;">🟢 FDR 1-2 (Easy)</span>
                <span style="background:#9e6a03; color:white; padding:4px 12px; border-radius:6px; font-size:0.85rem;">🟡 FDR 3 (Medium)</span>
                <span style="background:#b62324; color:white; padding:4px 12px; border-radius:6px; font-size:0.85rem;">🔴 FDR 4-5 (Hard)</span>
            </div>
            """, unsafe_allow_html=True)

            # Best fixture run chart
            st.markdown('<div class="section-header">🏆 Best Fixture Runs (Next 5 GW)</div>', unsafe_allow_html=True)
            st.caption("Lower average difficulty = easier run of fixtures")

            if diff_cols:
                fixture_grid['avg_difficulty'] = fixture_grid[diff_cols].mean(axis=1)
                best_fixtures = fixture_grid[['Team','avg_difficulty']].sort_values('avg_difficulty').head(10)

                fig_fix = px.bar(
                    best_fixtures,
                    x='avg_difficulty', y='Team',
                    orientation='h',
                    color='avg_difficulty',
                    color_continuous_scale=['#1a7f37','#9e6a03','#b62324'],
                    template='plotly_dark',
                    range_color=[1,5]
                )
                fig_fix.update_layout(
                    plot_bgcolor='#161b27', paper_bgcolor='#161b27',
                    font=dict(color='#e6edf3'), height=400,
                    margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=False
                )
                st.plotly_chart(fig_fix, use_container_width=True)


# ==============================
# TAB 4 — DIFFERENTIALS
# ==============================
with tab4:

    st.markdown('<div class="section-header">🎯 Differential Picks</div>', unsafe_allow_html=True)
    st.write("High predicted points but below average recent form — the model thinks these players are about to bounce back. Low ownership likely.")

    diff_df = filtered_df[
        (filtered_df['Predicted Points'] > filtered_df['Predicted Points'].mean()) &
        (filtered_df['last_5_avg'] < filtered_df['last_5_avg'].mean())
    ].sort_values('Predicted Points', ascending=False).head(10)

    if diff_df.empty:
        st.info("No differentials found with current filters.")
    else:
        diff_cols = ['Player','Position','Team','Predicted Points','last_3_avg','last_5_avg','now_cost']
        diff_display = diff_df[[c for c in diff_cols if c in diff_df.columns]].copy()
        diff_display['now_cost'] = (diff_display['now_cost'] / 10).round(1).astype(str) + "m"
        st.dataframe(diff_display, use_container_width=True, hide_index=True)

    # Scatter
    st.markdown('<div class="section-header">📈 Form vs Prediction</div>', unsafe_allow_html=True)
    fig_diff = px.scatter(
        filtered_df,
        x='last_3_avg',
        y='Predicted Points',
        hover_data=['Player','Team','Position'],
        color='Position',
        template='plotly_dark',
        color_discrete_map={'GK':'#58a6ff','DEF':'#3fb950','MID':'#e3b341','FWD':'#f85149'}
    )
    fig_diff.update_layout(
        plot_bgcolor='#161b27', paper_bgcolor='#161b27',
        font=dict(color='#e6edf3'), height=500,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_diff, use_container_width=True)


# ==============================
# TAB 5 — VALUE PICKS
# ==============================
with tab5:

    st.markdown('<div class="section-header">💰 Best Value for Money</div>', unsafe_allow_html=True)
    st.write("Highest predicted points relative to price. Essential for building a balanced squad.")

    value_df = filtered_df.sort_values('value_for_money', ascending=False).head(20).copy()
    val_cols = ['Player','Position','Team','Predicted Points','now_cost','value_for_money','last_5_avg']
    val_display = value_df[[c for c in val_cols if c in value_df.columns]].copy()
    val_display['now_cost'] = (val_display['now_cost'] / 10).round(1).astype(str) + "m"
    st.dataframe(val_display, use_container_width=True, hide_index=True)

    # Price vs Points scatter
    st.markdown('<div class="section-header">📊 Price vs Predicted Points</div>', unsafe_allow_html=True)
    st.caption("Bigger bubble = better value for money")

    fig_price = px.scatter(
        filtered_df,
        x='now_cost',
        y='Predicted Points',
        hover_data=['Player','Team','Position'],
        color='Position',
        size='value_for_money',
        template='plotly_dark',
        color_discrete_map={'GK':'#58a6ff','DEF':'#3fb950','MID':'#e3b341','FWD':'#f85149'}
    )
    fig_price.update_layout(
        plot_bgcolor='#161b27', paper_bgcolor='#161b27',
        font=dict(color='#e6edf3'), height=500,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_price, use_container_width=True)

    # Download
    st.download_button(
        label="⬇️ Download Value Picks as CSV",
        data=value_df.to_csv(index=False),
        file_name='fpl_value_picks.csv',
        mime='text/csv'
    )


# ==============================
# TAB 6 — MODEL ACCURACY
# ==============================
with tab6:

    st.markdown('<div class="section-header">📊 Model Accuracy</div>', unsafe_allow_html=True)

    if val_df.empty:
        st.warning("Validation data not available. Run model.py first.")
    else:
        # Filter by search
        display_val = val_df.copy()
        if player_search:
            display_val = display_val[
                display_val['Player'].str.contains(player_search, case=False)
            ]

        # MAE Metric
        if not display_val.empty:
            mae = (display_val['Actual Points'] - display_val['Predicted Points']).abs().mean()
            within_2 = len(display_val[
                abs(display_val['Actual Points'] - display_val['Predicted Points']) <= 2
            ]) / len(display_val) * 100

            acc_col1, acc_col2, acc_col3 = st.columns(3)
            acc_col1.metric("Mean Absolute Error", round(mae, 2),
                            help="Average points the model is off by. Lower = better.")
            acc_col2.metric("Predictions Within 2pts", f"{round(within_2, 1)}%",
                            help="% of predictions that were within 2 points of actual score.")
            acc_col3.metric("Players Evaluated", len(display_val))

        # Predicted vs Actual scatter
        st.markdown('<div class="section-header">Predicted vs Actual Points</div>', unsafe_allow_html=True)
        st.caption("Dots close to the red line = accurate predictions")

        if not display_val.empty:
            fig_acc = px.scatter(
                display_val,
                x='Actual Points',
                y='Predicted Points',
                hover_data=['Player'],
                template='plotly_dark',
                color_discrete_sequence=['#58a6ff']
            )
            max_val = max(display_val['Actual Points'].max(), display_val['Predicted Points'].max())
            fig_acc.add_shape(
                type='line', x0=0, y0=0, x1=max_val, y1=max_val,
                line=dict(dash='dash', color='#f85149', width=2)
            )
            fig_acc.update_layout(
                plot_bgcolor='#161b27', paper_bgcolor='#161b27',
                font=dict(color='#e6edf3'), height=500,
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_acc, use_container_width=True)

            # Error distribution
            st.markdown('<div class="section-header">Error Distribution</div>', unsafe_allow_html=True)
            display_val['error_signed'] = display_val['Predicted Points'] - display_val['Actual Points']
            fig_err = px.histogram(
                display_val,
                x='error_signed',
                nbins=30,
                template='plotly_dark',
                color_discrete_sequence=['#58a6ff'],
                title="How far off is the model? (negative = over-predicted, positive = under-predicted)"
            )
            fig_err.update_layout(
                plot_bgcolor='#161b27', paper_bgcolor='#161b27',
                font=dict(color='#e6edf3'), height=350,
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_err, use_container_width=True)

            # Validation Table
            st.markdown('<div class="section-header">📋 Player Results</div>', unsafe_allow_html=True)
            st.dataframe(
                display_val[['Player','Actual Points','Predicted Points','error']].sort_values('error'),
                use_container_width=True,
                hide_index=True
            )