# bread and butter
import calendar
from collections import defaultdict
import datetime
import numpy as np
import os
import pandas as pd
from pathlib import Path
import sys

# plotting utils
from bokeh.plotting import figure
from matplotlib import pyplot as plt 

# streamlit components
import streamlit as st

# my lib
from src.insights import fantasy_runs_comparison, fantasy_wickets_comparison, fantasy_points_comparison
from src.insights import fantasy_runs_scored_against_bowling, fantasy_wickets_taken_against_batting
from src.insights import fantasy_runs_scored_comparison, fantasy_wickets_taken_comparison

# Config variables
raw_data_path = "raw_data"
clean_data_path = "clean_data"

# Defining global utility maps
df_schedule = pd.read_csv(os.path.join(clean_data_path, "schedule.csv"))
df_schedule = df_schedule.loc[:, ~df_schedule.columns.str.contains('^Unnamed')]

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

def populate_opposition_bowlers(player, selected_match):
    # if there is no match on this date, return empty list
    if selected_match is None:
        return []
    
    team_1_id = team_id_map[selected_match.split(" vs ")[0]]
    team_2_id = team_id_map[selected_match.split(" vs ")[1]]
    current_year = str(datetime.date.today().year)
    players_team_1 = [player_id_name_map[int(player_id)] for player_id in df_squad[df_squad["team_id"] == team_1_id][current_year].iloc[0].split(",")]
    players_team_2 = [player_id_name_map[int(player_id)] for player_id in df_squad[df_squad["team_id"] == team_2_id][current_year].iloc[0].split(",")]
    
    players_bowling_types = defaultdict(list)
    
    if player in players_team_1:
        opposition_players = [player_name_id_map[player_name] for player_name in players_team_2]
    else:
        opposition_players = [player_name_id_map[player_name] for player_name in players_team_1]
        
    for opp_player in opposition_players:
        bowling_type = df_player[df_player["player_id"] == opp_player]["bowling_style"].iloc[0]
        if type(bowling_type) is not str:
            continue
        players_bowling_types[bowling_type].append(opp_player)
    
    list_players_bowling_types = [[player_id_name_map[player] for player in players] for bowl_type, players in players_bowling_types.items()]
    df_result = pd.DataFrame(list_players_bowling_types).transpose()
    df_result.columns = players_bowling_types.keys()
    
    return df_result

def populate_opposition_batters(player, selected_match):
    # if there is no match on this date, return empty list
    if selected_match is None:
        return []
    
    team_1_id = team_id_map[selected_match.split(" vs ")[0]]
    team_2_id = team_id_map[selected_match.split(" vs ")[1]]
    current_year = str(datetime.date.today().year)
    players_team_1 = [player_id_name_map[int(player_id)] for player_id in df_squad[df_squad["team_id"] == team_1_id][current_year].iloc[0].split(",")]
    players_team_2 = [player_id_name_map[int(player_id)] for player_id in df_squad[df_squad["team_id"] == team_2_id][current_year].iloc[0].split(",")]
    
    players_batting_types = defaultdict(list)
    
    if player in players_team_1:
        opposition_players = [player_name_id_map[player_name] for player_name in players_team_2]
    else:
        opposition_players = [player_name_id_map[player_name] for player_name in players_team_1]
        
    for opp_player in opposition_players:
        batting_type = df_player[df_player["player_id"] == opp_player]["batting_style"].iloc[0]
        if type(batting_type) is not str:
            continue
        players_batting_types[batting_type].append(opp_player)
    
    list_players_batting_types = [[player_id_name_map[player] for player in players] for bat_type, players in players_batting_types.items()]
    df_result = pd.DataFrame(list_players_batting_types).transpose()
    df_result.columns = players_batting_types.keys()
    
    return df_result

def main(match_format):
    st.title("Fantasy - UI Rough Design")
    st.markdown("Helping you pick your best Dream 11 team")
    
    # Main input section
                
    col1, col2 = st.beta_columns((1, 1))
    
    with col1:
        match_date = st.date_input("Match Date")
    
    with col2:
        selected_match = st.selectbox("Choose match", options=choose_matches(match_date))
        venue_selected_match = ""
        if selected_match:
            venue_selected_match = df_schedule[df_schedule['match_display_name'].str.contains(selected_match)]['venue'].iloc[0]
            st.write("Venue: ", venue_selected_match)
                
                
    col1, col2, col3 = st.beta_columns((1, 2, 1))
    
    with col2:
        players_list = st.multiselect("Choose players to compare:", options=populate_players(selected_match))  
            
    
    
    col1, col2, col3, col4 = st.beta_columns((1, 1, 1, 1))
    
    with col2:
        this_venue_bool = st.checkbox("In %s" % venue_selected_match)
        this_opposition_bool = st.checkbox("Against this opposition")
    
    with col3:
        innings_number = st.number_input("Innnings number: ", min_value=0, max_value=2, step=1, format="%d")
    
    col1, col2, col3 = st.beta_columns((1, 1, 1))
    
    with col1:
        if selected_match:
            stats = fantasy_runs_scored_comparison(players_list, selected_match, this_venue_bool, this_opposition_bool, innings_number)

            fig, ax = plt.subplots()
            y_pos = np.arange(len(players_list))
            hbars = ax.barh(y_pos, stats, height=0.25)
            for i, v in enumerate(stats):
                ax.text(v + 3, i+0.05, str(v), color='black')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(players_list)
            ax.invert_yaxis()  # labels read top-to-bottom
            ax.set_xlabel('Runs')
            ax.set_title('All time runs comparison')
            st.pyplot(fig)
    
    with col2:
        if selected_match:
            stats = fantasy_wickets_taken_comparison(players_list, selected_match, this_venue_bool, this_opposition_bool, innings_number)

            fig, ax = plt.subplots()
            y_pos = np.arange(len(players_list))
            hbars = ax.barh(y_pos, stats, height=0.25)
            for i, v in enumerate(stats):
                ax.text(v + 3, i+0.05, str(v), color='black')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(players_list)
            ax.invert_yaxis()  # labels read top-to-bottom
            ax.set_xlabel('Runs')
            ax.set_title('All time runs comparison')
            st.pyplot(fig)
            
    with col3:
        if selected_match:
            stats = fantasy_runs_scored_comparison(players_list, selected_match, this_venue_bool, this_opposition_bool, innings_number)

            fig, ax = plt.subplots()
            y_pos = np.arange(len(players_list))
            hbars = ax.barh(y_pos, stats, height=0.25)
            for i, v in enumerate(stats):
                ax.text(v + 3, i+0.05, str(v), color='black')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(players_list)
            ax.invert_yaxis()  # labels read top-to-bottom
            ax.set_xlabel('Runs')
            ax.set_title('All time runs comparison')
            st.pyplot(fig)
            
    col1, col2, col3 = st.beta_columns((1, 2, 1))
    
    with col2:
        recency_parameter = st.slider("Recency parameter ", min_value=1, max_value=20, value=1, step=1, format="%d")
    
    # Output section
    col1, col2, col3 = st.beta_columns((1, 1, 1))
    
    # Runs scored
    with col1:
        st.subheader("Runs Comparison")
        if len(players_list) > 0:
            st.line_chart(fantasy_runs_comparison(recency_parameter, players_list))
            
    # Wickets taken
    with col2:
        st.subheader("Wickets Comparison")
        if len(players_list) > 0:
            st.line_chart(fantasy_wickets_comparison(recency_parameter, players_list))
        
    # Fantasy points
    with col3:
        st.subheader("Points Comparison")
        if len(players_list) > 0:
            st.line_chart(fantasy_points_comparison(recency_parameter, players_list))
        
        '''
        if selected_match:
            stats = fantasy_wickets_taken_comparison(players_list, selected_match, this_venue_bool, this_opposition_bool, innings_number)

            fig, ax = plt.subplots()
            y_pos = np.arange(len(players_list))
            hbars = ax.barh(y_pos, stats, height=0.25)
            for i, v in enumerate(stats):
                ax.text(v + 3, i+0.05, str(v), color='black')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(players_list)
            ax.invert_yaxis()  # labels read top-to-bottom
            ax.set_xlabel('Runs')
            ax.set_title('All time wickets comparison')
            st.pyplot(fig)
    
    for player in players_list:
        st.header(player)
        col1, col2, col3, col4 = st.beta_columns((1, 1, 1, 1))

        # First pie chart -> Percentage distribution of runs scored with respect to bowling types
        with col1:
            st.subheader("Runs Scored vs Bowling Types")
            if len(players_list) > 0:
                st.bar_chart(fantasy_runs_scored_against_bowling(recency_parameter, player))
            
        # Table giving them information about who are the bowlers of the above types
        with col2:
            st.subheader("Bowlers in opposition")
            st.table(populate_opposition_bowlers(player, selected_match))

        # First pie chart -> Percentage distribution of runs scored with respect to bowling types
        with col3:
            st.subheader("Wickets Taken vs Batting Types")
            if len(players_list) > 0:
                st.bar_chart(fantasy_wickets_taken_against_batting(recency_parameter, player))
                
        # Table giving them information about who are the bowlers of the above types
        with col4:
            st.subheader("Batters in opposition")
            st.table(populate_opposition_batters(player, selected_match))
        
    
    
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