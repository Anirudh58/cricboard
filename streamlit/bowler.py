# bread and butter
import numpy as np
import os
import pandas as pd
from pathlib import Path
import sys

# streamlit components
import streamlit as st

# my lib
from src.insights import total_wickets, bowling_strike_rate, bowling_average

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
    players = np.array(df_player["player_name"])
    return players


@st.cache
def populate_tournaments(match_format):
    df_tournament = pd.read_csv(os.path.join(clean_data_path, "tournament.csv"))
    tournaments = np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])
    return tournaments


def main(match_format):
    st.title("Bowler - General")
        
    # Dividing the entire layout into 3 sections in the ratio 1:1:2
    col1, col2, col3 = st.beta_columns((1, 1, 1))
    
    # INPUT SECTION
    
    with col1:
        player_name = st.selectbox("Choose a single player:", options=populate_players())
        years_range = st.slider("The period you want to consider:", min_value=2000, max_value=2021, value=(2000, 2021), step=1, format="%d")
        overs_range = st.slider("The overs range you want to consider: ", min_value=0, max_value=20, value=(0,20), step=1, format="%d")
        lh_bat_bool = st.checkbox("Against LH Bat")
        rh_bat_bool = st.checkbox("Against RH Bat")
    
    with col2:
        top_n = st.number_input("Choose top n (enter 0 for single player stats): ", min_value=0, max_value=10, step=1, format="%d")
        venue = st.selectbox("Venue:", options=populate_venues())
        minimum_balls = st.number_input("Min balls bowled (for SR and Average): ", min_value=100, max_value=2000, step=1, format="%d")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        
    with col3:
        tournaments = st.multiselect("Tournaments:", options=populate_tournaments(match_format))        
        opposition = st.selectbox("Opposition: (TBD)", options=populate_teams())
        batsman_name = st.selectbox("Choose a batsman (TBD):", options=populate_players())
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")

    # OUTPUT SECTION
    
    with col1:
        st.header("Wickets")
        st.table(total_wickets(player_name=player_name, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range))

    with col2:
        st.header("Strike Rate")
        st.table(bowling_strike_rate(player_name=player_name, top_n=top_n, minimum_balls=minimum_balls, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range))

        
    with col3:
        st.header("Average")
        st.table(bowling_average(player_name=player_name, top_n=top_n, minimum_balls=minimum_balls, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range))


    