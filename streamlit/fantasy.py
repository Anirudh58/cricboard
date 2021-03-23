# bread and butter
import calendar
import datetime
from matplotlib import pyplot as plt 
import numpy as np
import os
import pandas as pd
from pathlib import Path
import sys

# streamlit components
import streamlit as st

# my lib
from src.insights import fantasy_runs_comparison, fantasy_wickets_comparison, fantasy_points_comparison

# Config variables
raw_data_path = "raw_data"
clean_data_path = "clean_data"

# Defining global utility maps
df_schedule = pd.read_csv(os.path.join(clean_data_path, "schedule.csv"))

df_team = pd.read_csv(os.path.join(clean_data_path, "team.csv"))
df_team = df_team.loc[:, ~df_team.columns.str.contains('^Unnamed')]
team_id_map = dict(zip(df_team.team_name, df_team.team_id))
team_id_map["Delhi Capitals"] = team_id_map["Delhi Daredevils"]
team_id_map["Punjab Kings"] = team_id_map["Kings XI Punjab"]

df_squad = pd.read_csv(os.path.join(clean_data_path, "squad.csv"))

df_player = pd.read_csv(os.path.join(clean_data_path, "player.csv"))
df_player = df_player.loc[:, ~df_player.columns.str.contains('^Unnamed')]
player_dispname_id_map = dict(zip(df_player.player_display_name, df_player.player_id))
player_name_id_map = dict(zip(df_player.player_name, df_player.player_id))
player_id_name_map = dict(zip(df_player.player_id, df_player.player_name))

@st.cache
def choose_matches(match_date):
    date_string = f"{match_date.day:02d}-{calendar.month_name[match_date.month][0:3].lower()}-{match_date.year}"
    match_display_names = np.array(df_schedule[df_schedule['time'].str.contains(date_string)]['match_display_name'])
    return match_display_names

@st.cache
def populate_players(selected_match):
    # if there is no match on this date, return empty list
    if selected_match is None:
        return []
    
    team_1_id = team_id_map[selected_match.split(" vs ")[0]]
    team_2_id = team_id_map[selected_match.split(" vs ")[1]]
    current_year = str(datetime.date.today().year)
    players_team_1 = [player_id_name_map[int(player_id)] for player_id in df_squad[df_squad["team_id"] == team_1_id][current_year].iloc[0].split(",")]
    players_team_2 = [player_id_name_map[int(player_id)] for player_id in df_squad[df_squad["team_id"] == team_2_id][current_year].iloc[0].split(",")]
    players_both_teams = players_team_1 + players_team_2
    return players_both_teams

def main(match_format):
    st.title("Fantasy - UI Rough Design")
    st.markdown("Helping you pick your best Dream 11 team")
                
    col1, col2 = st.beta_columns((1, 1))
    
    with col1:
        match_date = st.date_input("Match Date")
    
    with col2:
        selected_match = st.selectbox("Choose match", options=choose_matches(match_date))
                
                
    col1, col2, col3 = st.beta_columns((1, 2, 1))
    
    with col2:
        players_list = st.multiselect("Choose upto 5 players to compare:", options=populate_players(selected_match))  
        
        
    col1, col2, col3 = st.beta_columns((1, 2, 1))
    
    with col2:
        recency_parameter = st.slider("Recency parameter ", min_value=1, max_value=20, value=1, step=1, format="%d")
                
    col1, col2, col3 = st.beta_columns((1, 1, 1))
    
    # Runs scored
    with col1:
        st.header("Runs Comparison")
        st.line_chart(fantasy_runs_comparison(recency_parameter, players_list))
        
    # Wickets taken
    with col2:
        st.header("Wickets Comparison")
        st.line_chart(fantasy_wickets_comparison(recency_parameter, players_list))
        
    # Fantasy points
    with col3:
        st.header("Points Comparison")
        st.line_chart(fantasy_points_comparison(recency_parameter, players_list))
        
    
    for player in players_list:
        st.header(player)
        col1, col2, col3, col4 = st.beta_columns((1, 1, 1, 1))

        # First pie chart -> Percentage distribution of runs scored with respect to bowling types
        with col1:
            st.subheader("Runs Scored vs Bowling")

            # Creating dataset 
            bowling_types = ['LEFT SPIN', 'RIGHT ARM PACE', 'LEFT ARM PACE'] 
            values = [23, 17, 35] 

            # Creating plot 
            fig = plt.figure(figsize =(6, 4)) 
            plt.pie(values, labels = bowling_types) 

            st.pyplot(fig)

        # Table giving them information about who are the bowlers of the above types
        with col2:
            st.subheader("Bowlers in opposition")
            bowlers = pd.DataFrame([["JADDU", "BOOM", "NATTU"]], columns=['LEFT SPIN', 'RIGHT ARM PACE', 'LEFT ARM PACE'])
            st.table(bowlers)

        # First pie chart -> Percentage distribution of runs scored with respect to bowling types
        with col3:
            st.subheader("Wickets taken vs Batting")

            # Creating dataset 
            batting_types = ['LHB', 'RHB'] 
            values = [40, 60] 

            # Creating plot 
            fig = plt.figure(figsize =(6, 4))
            plt.pie(values, labels = batting_types) 

            st.pyplot(fig)

        # Table giving them information about who are the bowlers of the above types
        with col4:
            st.subheader("Batters in opposition")
            batters = pd.DataFrame([["PADIKKAL", "KOHLI"]], columns=['LHB', 'RHB'] )
            st.table(batters)
        
    
    '''
    col1, col2, col3, col4 = st.beta_columns((1, 1, 1, 1))
        
        
    # First pie chart -> Percentage distribution of runs scored with respect to bowling types
    with col1:
        st.header("Wickets taken vs Batting")
        
        # Creating dataset 
        batting_types = ['LHB', 'RHB'] 
        values = [40, 60] 

        # Creating plot 
        fig = plt.figure(figsize =(6, 4))
        plt.pie(values, labels = batting_types) 
        
        st.pyplot(fig)
        
    # Table giving them information about who are the bowlers of the above types
    with col2:
        
        st.header("Batters in opposition")
        batters = pd.DataFrame([["PADIKKAL", "KOHLI"]], columns=['LHB', 'RHB'] )
        st.table(batters)
        
        
    # First pie chart -> Percentage distribution of runs scored with respect to bowling types
    with col3:
        st.header("Wickets taken vs Batting")
        
        # Creating dataset 
        batting_types = ['LHB', 'RHB'] 
        values = [60, 40] 

        # Creating plot 
        fig = plt.figure(figsize =(6, 4))
        plt.pie(values, labels = batting_types) 
        
        st.pyplot(fig)
        
    # Table giving them information about who are the bowlers of the above types
    with col4:
        
        st.header("Batters in opposition")
        batters = pd.DataFrame([["PADIKKAL", "KOHLI"]], columns=['LHB', 'RHB'] )
        st.table(batters)
    '''