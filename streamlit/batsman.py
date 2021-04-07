# bread and butter
import numpy as np
import os
import pandas as pd
from pathlib import Path
import sys

# streamlit components
import streamlit as st

# my lib
from src.insights import batting_total_runs, batting_strike_rate, batting_average, batting_dismissals


# Config variables
raw_data_path = "raw_data"
clean_data_path = "clean_data"

@st.cache
def populate_venues():
    df_venue = pd.read_csv(os.path.join(clean_data_path, "venue.csv"))
    venues = ["ALL"]
    venues.extend(np.array(df_venue["venue_name"]))
    return venues

@st.cache
def populate_teams():
    df_team = pd.read_csv(os.path.join(clean_data_path, "team.csv"))
    teams = ["ALL"]
    teams.extend(np.array(df_team["team_name"]))
    return teams

@st.cache
def populate_players():
    df_player = pd.read_csv(os.path.join(clean_data_path, "player.csv"))
    players = ['']
    players.extend(sorted(np.array(df_player[~df_player['player_display_name'].isnull()]['player_name'])))
    return players

@st.cache
def populate_bowlers():
    df_player = pd.read_csv(os.path.join(clean_data_path, "player.csv"))
    bowlers = ["ALL"]
    bowlers.extend(sorted(np.array(df_player[~df_player['player_display_name'].isnull()]['player_name'])))
    return bowlers


@st.cache
def populate_tournaments(match_format):
    df_tournament = pd.read_csv(os.path.join(clean_data_path, "tournament.csv"))
    tournaments = np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])
    return tournaments


def main(match_format, session_state):
    st.title("Batting Stats")
        
    # Dividing the entire layout into 3 sections in the ratio 1:1:2
    col1, col2, col3 = st.beta_columns((1, 1, 1))
    
    # INPUT SECTION
    
    with col1:
        player_name = st.selectbox("Choose player: (will be overriden when 'Top n' > 0)", options=populate_players())
        years_range = st.slider("The period you want to consider:", min_value=2000, max_value=2021, value=(2000, 2021), step=1, format="%d")
        overs_range = st.slider("The overs range you want to consider: ", min_value=0, max_value=20, value=(0,20), step=1, format="%d")
        only_pace_bool = st.checkbox("Against Pace")
        right_arm_pace_bool = st.checkbox("Against right_arm_pace")
        left_arm_pace_bool = st.checkbox("Against left_arm_pace")

        st.write("\n")
    
    with col2:
        top_n = st.number_input("Top n performers (0 for single player stats): ", min_value=0, max_value=10, step=1, format="%d")
        venue = st.selectbox("Venue:", options=populate_venues())
        minimum_runs = st.number_input("Min runs scored (for SR and Average): ", min_value=100, max_value=2000, step=1, format="%d")
        only_spin_bool = st.checkbox("Against Spin")
        right_arm_wrist_spin_bool = st.checkbox("Against right_arm_wrist_spin")
        right_arm_off_spin_bool = st.checkbox("Against right_arm_off_spin")
        left_arm_orthodox_bool = st.checkbox("Against left_arm_orthodox")
        left_arm_wrist_bool = st.checkbox("Against left_arm_wrist")
        st.write("\n")
        
    with col3:
        tournaments = st.multiselect("Tournaments:", options=populate_tournaments(match_format))        
        innings_number = st.number_input("Innnings number: (0 -> both) ", min_value=0, max_value=2, step=1, format="%d")
        bowler_name = st.selectbox("Against a specific bowler:", options=populate_bowlers())
        

    # OUTPUT SECTION
    
    bowling_types = {
        "right_arm_pace_bool" : right_arm_pace_bool,
        "left_arm_pace_bool" : left_arm_pace_bool,
        "right_arm_wrist_spin_bool" : right_arm_wrist_spin_bool,
        "right_arm_off_spin_bool" : right_arm_off_spin_bool,
        "left_arm_orthodox_bool" : left_arm_orthodox_bool,
        "left_arm_wrist_bool" : left_arm_wrist_bool
    }
    
    col1, col2, col3, col4 = st.beta_columns((1, 1, 1, 1))
    
    
    if player_name or top_n > 0:
        with col1:
            st.header("Runs")
            st.table(batting_total_runs(player_name=player_name, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_spin=only_spin_bool, against_pace=only_pace_bool, bowling_types=bowling_types, against_bowler=bowler_name, innings_number=innings_number))

        with col2:
            st.header("Strike Rate")
            st.table(batting_strike_rate(player_name=player_name, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_spin=only_spin_bool, against_pace=only_pace_bool, bowling_types=bowling_types, against_bowler=bowler_name, minimum_runs=minimum_runs, innings_number=innings_number))

        with col3:
            st.header("Average")
            st.table(batting_average(player_name=player_name, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_spin=only_spin_bool, against_pace=only_pace_bool, bowling_types=bowling_types, against_bowler=bowler_name, minimum_runs=minimum_runs, innings_number=innings_number))

        with col4:
            st.header("Dismissals")
            st.table(batting_dismissals(player_name=player_name, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_spin=only_spin_bool, against_pace=only_pace_bool, bowling_types=bowling_types, against_bowler=bowler_name, innings_number=innings_number))
    
    