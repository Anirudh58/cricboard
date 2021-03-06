import numpy as np
import pandas as pd
import streamlit as st

from insights import total_runs, strike_rate

@st.cache
def populate_venues():
    df_venue = pd.read_csv("./clean_data/venue.csv")
    venues = ["ALL"]
    venues.extend(np.array(df_venue["venue_name"]))
    return venues

@st.cache
def populate_teams():
    df_team = pd.read_csv("./clean_data/team.csv")
    teams = ["ALL"]
    teams.extend(np.array(df_team["team_name"]))
    return teams

@st.cache
def populate_players():
    df_player = pd.read_csv("./clean_data/player.csv")
    players = np.array(df_player["player_name"])
    return players


@st.cache
def populate_tournaments(match_format):
    df_tournament = pd.read_csv("./clean_data/tournament.csv")
    tournaments = np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])
    return tournaments



def main(match_format):
    st.title("Batsman")
    #st.markdown("This page will contain some general stats specific to batting")
    
    '''
    Each insight is going to consist of the following sections
    1) header - Name of the stat
    2) markdown - Brief description of the stat
    3) input section - a section where the parameters to the stat can be interactively controlled
    4) output section - a section where the output is displayed in some cool UI (if possible)
    '''
    
    # Stat info
    st.header("Total Runs")
    
    # Dividing the entire layout into 3 sections in the ratio 1:1:2
    col1, col2, col3 = st.beta_columns((1, 1, 2))
    
    # Input sections
    with col1:
        
        # player name
        player_name = st.selectbox("Choose a single player:", options=populate_players())
        
        # years range
        years_range = st.slider("The period you want to consider:", min_value=2000, max_value=2021, 
                            value=(2000, 2021), step=1, format="%d")
        #st.write(f"years_range: {[year for year in range(years_range[0], years_range[1]+1)]}")
        
        # overs_range
        overs_range = st.slider("The overs range you want to consider: ", min_value=0, max_value=20, 
                                value=(0,20), step=1, format="%d")
        #st.write(f"overs_range: {overs_range}")
        
        # against pace bowling types
        la_pace_bool = st.checkbox("Against LA Pace")
        ra_pace_bool = st.checkbox("Against RA Pace")
        # against spin bowling types
        la_spin_bool = st.checkbox("Against LA Spin")
        ra_spin_bool = st.checkbox("Against RA Spin")
        
        #st.write(f"la_pace_bool: {la_pace_bool}, ra_pace_bool: {ra_pace_bool}, la_spin_bool: {la_spin_bool}, ra_spin_bool: {ra_spin_bool}")
        
        # top_n
        minimum_runs = st.number_input("Min runs scored (for SR): ", min_value=1, max_value=2000, step=1, format="%d")
    
    
    with col2:
        
        # top_n
        top_n = st.number_input("Choose top n: ", min_value=0, max_value=10, step=1, format="%d")
        #st.write(f"top_n: {top_n}")
        
        # venue
        venue = st.selectbox("Venue:", options=populate_venues())
        
        # opposition
        opposition = st.selectbox("Opposition: (TBD)", options=populate_teams())

        # batting positon
        batting_position = st.number_input("Batting position: (TBD)", min_value=1, max_value=11, step=1, format="%d")
        #st.write(f"batting_position: {batting_position}")
        
        # tournament
        tournaments = st.multiselect("Tournaments:", options=populate_tournaments(match_format))
        #st.write(f"tournaments: {tournaments}")
    
    # Output sections
    with col3:
        
        # total runs
        st.header("Runs")
        st.table(total_runs(player_name=player_name, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range))
        
        # total runs
        st.header("Strike Rate")
        st.table(strike_rate(player_name=player_name, top_n=top_n, match_format=match_format, minimum_runs=minimum_runs, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range))
    
    # Output section