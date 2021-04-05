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
from matplotlib import pyplot as plt 

# streamlit components
import streamlit as st

# my lib
from src.insights import fantasy_runs_comparison, fantasy_wickets_comparison, fantasy_points_comparison
from src.insights import fantasy_runs_scored_against_bowling, fantasy_wickets_taken_against_batting
from src.insights import fantasy_runs_scored_comparison, fantasy_wickets_taken_comparison, fantasy_points_obtained_comparison

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

df_venue = pd.read_csv(os.path.join(clean_data_path, "venue.csv"))
df_venue = df_venue.loc[:, ~df_venue.columns.str.contains('^Unnamed')]
venue_id_map = dict(zip(df_venue.venue_name, df_venue.venue_id))
venue_location_name_map = dict(zip(df_venue.venue_location, df_venue.venue_name))

@st.cache
def choose_matches(match_date):
    date_string = f"{match_date.day:02d}-{calendar.month_name[match_date.month][0:3].lower()}-{match_date.year}"
    match_display_names = np.array(df_schedule[df_schedule['time'].str.contains(date_string)]['match_display_name'])
    return match_display_names

@st.cache
def choose_match_teams(selected_match):
    team_1 = selected_match.split(" vs ")[0]
    team_2 = selected_match.split(" vs ")[1]
    return (team_1, team_2)

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

def populate_opposition_bowlers(selected_match, bowling_types):
    # if there is no match on this date, return empty list
    if selected_match is None:
        return []
    
    team_1 = selected_match.split(" vs ")[0]
    team_2 = selected_match.split(" vs ")[1]
    team_1_id = team_id_map[team_1]
    team_2_id = team_id_map[team_2]
    current_year = str(datetime.date.today().year)
    players_team_1 = df_squad[df_squad["team_id"] == team_1_id][current_year].iloc[0].split(",")
    players_team_2 = df_squad[df_squad["team_id"] == team_2_id][current_year].iloc[0].split(",")
    
    players_team_1_bowling_types = {}
    players_team_2_bowling_types = {}
    for bowling_type in bowling_types:
        players_team_1_bowling_types[bowling_type.replace('\n', '')] = ''
        players_team_2_bowling_types[bowling_type.replace('\n', '')] = ''
        
    for player in players_team_1:
        bowling_type = df_player[df_player["player_id"] == int(player)]["bowling_style"].iloc[0]
        if type(bowling_type) is not str:
            continue
        players_team_1_bowling_types[bowling_type] += (player_id_name_map[int(player)] + '\n')

    for player in players_team_2:
        bowling_type = df_player[df_player["player_id"] == int(player)]["bowling_style"].iloc[0]
        if type(bowling_type) is not str:
            continue
        players_team_2_bowling_types[bowling_type] += (player_id_name_map[int(player)] + '\n')

    players_bowling_types = [players_team_1_bowling_types, players_team_2_bowling_types]
    df_result = pd.DataFrame(players_bowling_types, index =[team_1, team_2])
    return df_result

def populate_opposition_batters(selected_match, batting_types):
    # if there is no match on this date, return empty list
    if selected_match is None:
        return []
    team_1 = selected_match.split(" vs ")[0]
    team_2 = selected_match.split(" vs ")[1]
    team_1_id = team_id_map[team_1]
    team_2_id = team_id_map[team_2]
    current_year = str(datetime.date.today().year)
    players_team_1 = df_squad[df_squad["team_id"] == team_1_id][current_year].iloc[0].split(",")
    players_team_2 = df_squad[df_squad["team_id"] == team_2_id][current_year].iloc[0].split(",")
    
    players_team_1_batting_types = {}
    players_team_2_batting_types = {}
    for batting_type in batting_types:
        players_team_1_batting_types[batting_type.replace('\n', '')] = ''
        players_team_2_batting_types[batting_type.replace('\n', '')] = ''

    for player in players_team_1:
        batting_type = df_player[df_player["player_id"] == int(player)]["batting_style"].iloc[0]
        if type(batting_type) is not str:
            continue
        players_team_1_batting_types[batting_type] += (player_id_name_map[int(player)] + '\n')

    for player in players_team_2:
        batting_type = df_player[df_player["player_id"] == int(player)]["batting_style"].iloc[0]
        if type(batting_type) is not str:
            continue
        players_team_2_batting_types[batting_type] += (player_id_name_map[int(player)] + '\n')

    players_batting_types = [players_team_1_batting_types, players_team_2_batting_types]
    df_result = pd.DataFrame(players_batting_types, index =[team_1, team_2])
    return df_result

def main(match_format):
    st.title("Fantasy")
    st.markdown("Helping you pick your best Dream 11 team")
    
    # Main input section
                
    col1, col2 = st.beta_columns((1, 1))
    
    with col1:
        match_date = st.date_input("Match Date")
    
    with col2:
        selected_match = st.selectbox("Choose match", options=choose_matches(match_date))
        venue_selected_match = ""
        if selected_match:
            venue_selected_match = venue_location_name_map[df_schedule[df_schedule['match_display_name'].str.contains(selected_match)]['venue'].iloc[0]]
            #st.write("Venue: ", venue_selected_match)
                
                
    col1, col2, col3 = st.beta_columns((1, 2, 1))
    
    with col2:
        players_list = st.multiselect("Choose players to compare:", options=populate_players(selected_match))  

    if len(players_list) == 0:
        return
                
    col1, col2, col3 = st.beta_columns((10, 9, 10))

    with col2:
        st.header("ALL-TIME STATS COMPARISON")
        
    col1, col2, col3, col4 = st.beta_columns((1, 1, 1, 1))
    
    with col2:
        this_venue_bool = st.checkbox("In %s" % venue_selected_match)
        this_opposition_bool = st.checkbox("Against this opposition")
    
    with col3:
        this_innings_bool = st.checkbox("Filter by innings number")
        if this_innings_bool:
            batting_first_team = st.selectbox("Batting First Team: ", options=choose_match_teams(selected_match))
            batting_first_team = team_id_map[batting_first_team]
        else:
            batting_first_team = 0
    
    col1, col2, col3 = st.beta_columns((1, 1, 1))
    
    with col1:
        stats = fantasy_runs_scored_comparison(players_list, selected_match, this_venue_bool, this_opposition_bool, batting_first_team)

        fig, ax = plt.subplots()
        y_pos = np.arange(len(players_list))
        hbars = ax.barh(y_pos, stats, height=0.25)
        for i, v in enumerate(stats):
            ax.text(v, i+0.05, str(v), color='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(players_list)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Runs per Match')
        ax.set_title('All time runs comparison')
        st.pyplot(fig)
    
    with col2:
        stats = fantasy_wickets_taken_comparison(players_list, selected_match, this_venue_bool, this_opposition_bool, batting_first_team)

        fig, ax = plt.subplots()
        y_pos = np.arange(len(players_list))
        hbars = ax.barh(y_pos, stats, height=0.25)
        for i, v in enumerate(stats):
            ax.text(v, i+0.05, str(v), color='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(players_list)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Wickets per Match')
        ax.set_title('All time wickets comparison')
        st.pyplot(fig)
            
    with col3:
        stats = fantasy_points_obtained_comparison(players_list, selected_match, this_venue_bool, this_opposition_bool, batting_first_team)

        fig, ax = plt.subplots()
        y_pos = np.arange(len(players_list))
        hbars = ax.barh(y_pos, stats, height=0.25)
        for i, v in enumerate(stats):
            ax.text(v, i+0.05, str(v), color='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(players_list)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Points per Match')
        ax.set_title('All time points comparison')
        st.pyplot(fig)
            
    col1, col2, col3 = st.beta_columns((10, 9, 10))
    
    with col2:
        st.header("RECENT FORM COMPARISON")
            
    col1, col2, col3 = st.beta_columns((1, 2, 1))
    
    with col2:
        recency_parameter = st.slider("Recency parameter (Past n matches) ", min_value=1, max_value=20, value=3, step=1, format="%d")
    
    # Output section
    col1, col2, col3 = st.beta_columns((1, 1, 1))
    
    # Runs scored
    with col1:
        player_runs = fantasy_runs_comparison(recency_parameter, players_list)
        fig, ax = plt.subplots()
        plot_handles = []
        for i in range(len(players_list)):
            p, = ax.plot(range(1, recency_parameter+1), player_runs[i], label=players_list[i])
            plot_handles.append(p)
        ax.legend(handles=plot_handles, bbox_to_anchor=(1.01, 1), loc='upper left', prop={'size': 7})
        ax.set_title('Runs Comparison (Recent Form)')
        ax.set_xlabel('Matches')
        ax.set_ylabel('Runs')
        st.pyplot(fig)
    
    # Wickets taken
    with col2:
        player_wickets = fantasy_wickets_comparison(recency_parameter, players_list)
        fig, ax = plt.subplots()
        plot_handles = []
        for i in range(len(players_list)):
            p, = ax.plot(range(1, recency_parameter+1), player_wickets[i], label=players_list[i])
            plot_handles.append(p)
        ax.legend(handles=plot_handles, bbox_to_anchor=(1.01, 1), loc='upper left', prop={'size': 7})
        ax.set_title('Wickets Comparison (Recent Form)')
        ax.set_xlabel('Matches')
        ax.set_ylabel('Wickets')
        st.pyplot(fig)
        
    # Fantasy points
    with col3:
        player_points = fantasy_points_comparison(recency_parameter, players_list)
        fig, ax = plt.subplots()
        plot_handles = []
        for i in range(len(players_list)):
            p, = ax.plot(range(1, recency_parameter+1), player_points[i], label=players_list[i])
            plot_handles.append(p)
        ax.legend(handles=plot_handles, bbox_to_anchor=(1.01, 1), loc='upper left', prop={'size': 7})
        ax.set_title('Points Comparison (Recent Form)')
        ax.set_xlabel('Matches')
        ax.set_ylabel('Points')
        st.pyplot(fig)
    
    col1, col2, col3 = st.beta_columns((1, 2, 1))
    with col2:
        st.header("PLAYER SKILL ANALYSIS")

    col1, col2 = st.beta_columns((1, 1))

    with col1:
        bowling_types = ["Right arm \nOff spin", "Left arm \nOrthodox", "Right arm\n wrist spin", "Right arm\n Pace", "Left arm\n Pace", "Left arm\n wrist"]
        player_runs = fantasy_runs_scored_against_bowling(players_list)
        fig, ax = plt.subplots()
        # Get some pastel shades for the colors
        colors = plt.cm.Blues(np.linspace(0.25, 0.75, len(players_list)))

        index = np.arange(len(bowling_types)) # the x locations for the groups
        width = 0.35

        y_offset = np.zeros(len(bowling_types))
        cell_text = []
        for row in range(len(player_runs)):
            ax.bar(index, player_runs[row], width, color=colors[row], bottom=y_offset)
            y_offset = y_offset + player_runs[row]
            cell_text.append(player_runs[row])

        '''players_bowling_type = populate_opposition_bowlers(selected_match, bowling_types)
        table = ax.table(cellText=players_bowling_type.values,
                         colLabels=bowling_types,
                         loc='bottom')
        cellDict = table.get_celld()
        for i in range(0,len(players_bowling_type.columns)):
            cellDict[(0,i)].set_height(.01)'''

        table = ax.table(cellText=cell_text,
                         rowLabels=players_list,
                         rowColours=colors,
                         colLabels=bowling_types,
                         loc='bottom')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)

        ax.set_ylabel("Runs scored")
        ax.set_xticks([])
        ax.set_title('Runs Comparison(Bowler Types)')
        st.pyplot(fig)

    with col2:
        batting_types = ["Left-hand bat", "Right-hand bat"]
        player_wickets = fantasy_wickets_taken_against_batting(players_list)
        fig, ax = plt.subplots()
        # Get some pastel shades for the colors
        colors = plt.cm.Blues(np.linspace(0.25, 0.75, len(players_list)))

        index = np.arange(len(batting_types)) # the x locations for the groups
        width = 0.35

        y_offset = np.zeros(len(batting_types))
        cell_text = []
        for row in range(len(player_wickets)):
            ax.bar(index, player_wickets[row], width, color=colors[row], bottom=y_offset)
            y_offset = y_offset + player_wickets[row]
            cell_text.append(player_wickets[row])

        table = ax.table(cellText=cell_text,
                         rowLabels=players_list,
                         rowColours=colors,
                         colLabels=batting_types,
                         loc='bottom')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)

        ax.set_ylabel("Wickets taken")
        ax.set_xticks([])
        ax.set_title('Wickets Comparison(Batting Types)')
        st.pyplot(fig)
    
    '''
    #OLD UI
        
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