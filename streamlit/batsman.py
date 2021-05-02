# bread and butter
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
from src.insights import batting_total_runs, batting_strike_rate, batting_average, batting_dismissals, batting_balls_batted, batting_dot_balls_batted


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
def populate_stats():
    stats = ["", "Total Runs", "Strike Rate", "Average", "Dismissals", "Total Balls Batted", "Total Dot Balls"]
    return stats


@st.cache
def populate_tournaments(match_format):
    df_tournament = pd.read_csv(os.path.join(clean_data_path, "tournament.csv"))
    tournaments = np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])
    return tournaments

def draw_batting_plots(stats, metric, plot_summary):
    """
    Utility function to draw the batting plots
    Args:
        stats - (dataframe) the stats you wanna plot
        metric - (string) the type of stat
        plot_summary - (string) a string that describes the plot
    """
                
    fig, ax = plt.subplots()

    # plot configs
    colors = plt.cm.tab10(np.linspace(0.1, 0.9, len(stats)))
    x_pos = np.arange(1)
    width = 0.7 / len(stats)
    gap = 0.2 / len(stats)
    x_offset = 0

    cellTexts = []
    rowLabels = []

    for ind, row in stats.iterrows():
        ax.bar(x_pos+x_offset, row[metric], width, color=colors[ind])
        x_offset += (width + gap)
        cellTexts.append([str(round(row[metric],2))])
        rowLabels.append(row['player_name'])

    ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    table = ax.table(cellText=cellTexts, rowLabels=rowLabels, rowColours=colors, loc='bottom', colLabels=[metric.upper()], cellLoc='center')

    plt.title(plot_summary)
    table.scale(1, 2)
    st.pyplot(fig)
    
def get_plot_summary(metric, top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_runs, bowler_name, only_pace_bool, only_spin_bool, right_arm_pace_bool, left_arm_pace_bool, 
                     right_arm_wrist_spin_bool, right_arm_off_spin_bool, left_arm_orthodox_bool, left_arm_wrist_bool):
    """
    Takes a bunch of inputs and generates a string that is used for plot titles
    """
    
    if metric=='runs':
        plot_summary = "Total Runs scored by players "    
    elif metric=='strike_rate':
        plot_summary = "Strike Rate of players " 
        # min runs threshold
        if top_n != 0:
            plot_summary += ("\nMin Runs: " + str(minimum_runs))
    elif metric=='average':
        plot_summary = "Average of players " 
        # min runs threshold
        if top_n != 0:
            plot_summary += ("\nMin Runs: " + str(minimum_runs))
    elif metric=='dismissals':
        plot_summary = "Number of Dismissals " 
    elif metric=="balls_batted":
        plot_summary = "Total Balls Faced " 
    elif metric=="dot_balls_batted":
        plot_summary = "Total Dot Balls Batted " 
    
    # tournaments
    if len(tournaments) > 0 :
        plot_summary += ("\nIn Tournaments: " + ",".join([tournament for tournament in tournaments]))
    # venue
    if venue != 'ALL':
        plot_summary += ("\nIn Venue: " + venue)
    # period
    if years_range != (2000, 2021):
        plot_summary += ("\nBetween years: " + str(years_range[0]) + "-" + str(years_range[1]))
    # overs_range
    if overs_range != (0, 20):
        plot_summary += ("\nBetween overs: " + str(overs_range[0]) + "-" + str(overs_range[1]))
    # innings number
    if innings_number != 0:
        if innings_number == 1:
            plot_summary += ("\nBatting first")
        elif innings_number == 2:
            plot_summary += ("\nBatting second")
    # against bowler
    if bowler_name != 'ALL':
        plot_summary += ("\nAgainst bowler: " + bowler_name)
    # against bowling types (broad)
    if only_pace_bool or only_spin_bool:
        if only_pace_bool:
            plot_summary += ("\nAgainst Pace")
        elif only_spin_bool:
            plot_summary += ("\nAgainst Spin")
    # against bowling types (specific)
    if right_arm_pace_bool or left_arm_pace_bool or right_arm_wrist_spin_bool or right_arm_off_spin_bool or left_arm_orthodox_bool or left_arm_wrist_bool:
        if right_arm_pace_bool:
            plot_summary += ("\nAgainst Right Arm Pace")
        elif left_arm_pace_bool:
            plot_summary += ("\nAgainst Left Arm Pace")
        elif right_arm_wrist_spin_bool:
            plot_summary += ("\nAgainst Right Arm Wrist")
        elif right_arm_off_spin_bool:
            plot_summary += ("\nAgainst Right Arm Off")
        elif left_arm_orthodox_bool:
            plot_summary += ("\nAgainst Left Arm Orthodox")
        elif left_arm_wrist_bool:
            plot_summary += ("\nAgainst Left Arm Wrist")
            
    return plot_summary
            

def main(match_format, session_state):
    st.title("Batting Stats")
        
    # Dividing the entire layout into 3 sections in the ratio 1:1:2
    col1, col2, col3 = st.beta_columns((1, 1, 1))
    
    # INPUT SECTION
    
    with col1:
        player_name_list = st.multiselect("Choose player: (will be overriden when 'Top n' > 0)", options=populate_players())
        years_range = st.slider("The period you want to consider:", min_value=2000, max_value=2021, value=(2000, 2021), step=1, format="%d")
        overs_range = st.slider("The overs range you want to consider: ", min_value=0, max_value=20, value=(0,20), step=1, format="%d")
        only_pace_bool = st.checkbox("Against Pace")
        right_arm_pace_bool = st.checkbox("Against right_arm_pace")
        left_arm_pace_bool = st.checkbox("Against left_arm_pace")

        st.write("\n")
    
    with col2:
        top_n = st.number_input("Top n (0 for single player stats): ", min_value=0, max_value=10, step=1, format="%d")
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
            
    col1, col2, col3 = st.beta_columns((1, 3, 1))
    
    with col2:
        stat_to_show = st.selectbox("Choose stat:", options=populate_stats())  
        

    # OUTPUT SECTION
    
    bowling_types = {
        "right_arm_pace_bool" : right_arm_pace_bool,
        "left_arm_pace_bool" : left_arm_pace_bool,
        "right_arm_wrist_spin_bool" : right_arm_wrist_spin_bool,
        "right_arm_off_spin_bool" : right_arm_off_spin_bool,
        "left_arm_orthodox_bool" : left_arm_orthodox_bool,
        "left_arm_wrist_bool" : left_arm_wrist_bool
    }
    
    if player_name_list or top_n > 0:
        
        col1, col2, col3 = st.beta_columns((1, 2, 1))
        
        with col2:
            
            if stat_to_show == "Total Runs":
                players_stats = batting_total_runs(player_names=player_name_list, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_spin=only_spin_bool, against_pace=only_pace_bool, bowling_types=bowling_types, against_bowler=bowler_name, innings_number=innings_number)
                plot_summary = get_plot_summary('runs', top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_runs, bowler_name, only_pace_bool, only_spin_bool, right_arm_pace_bool, left_arm_pace_bool, right_arm_wrist_spin_bool, right_arm_off_spin_bool, left_arm_orthodox_bool, left_arm_wrist_bool)
                draw_batting_plots(players_stats, 'runs', plot_summary)
                
            elif stat_to_show == "Strike Rate":
                players_stats = batting_strike_rate(player_names=player_name_list, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_spin=only_spin_bool, against_pace=only_pace_bool, bowling_types=bowling_types, against_bowler=bowler_name, minimum_runs=minimum_runs, innings_number=innings_number)
                plot_summary = get_plot_summary('strike_rate', top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_runs, bowler_name, only_pace_bool, only_spin_bool, right_arm_pace_bool, left_arm_pace_bool, right_arm_wrist_spin_bool, right_arm_off_spin_bool, left_arm_orthodox_bool, left_arm_wrist_bool)
                draw_batting_plots(players_stats, 'strike_rate', plot_summary)
                
            elif stat_to_show == "Average":
                players_stats = batting_average(player_names=player_name_list, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_spin=only_spin_bool, against_pace=only_pace_bool, bowling_types=bowling_types, against_bowler=bowler_name, minimum_runs=minimum_runs, innings_number=innings_number)
                plot_summary = get_plot_summary('average', top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_runs, bowler_name, only_pace_bool, only_spin_bool, right_arm_pace_bool, left_arm_pace_bool, right_arm_wrist_spin_bool, right_arm_off_spin_bool, left_arm_orthodox_bool, left_arm_wrist_bool)
                draw_batting_plots(players_stats, 'average', plot_summary)
                
            elif stat_to_show == "Dismissals":
                players_stats = batting_dismissals(player_names=player_name_list, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_spin=only_spin_bool, against_pace=only_pace_bool, bowling_types=bowling_types, against_bowler=bowler_name, innings_number=innings_number)
                plot_summary = get_plot_summary('dismissals', top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_runs, bowler_name, only_pace_bool, only_spin_bool, right_arm_pace_bool, left_arm_pace_bool, right_arm_wrist_spin_bool, right_arm_off_spin_bool, left_arm_orthodox_bool, left_arm_wrist_bool)
                draw_batting_plots(players_stats, 'dismissals', plot_summary)
            
            elif stat_to_show == "Total Balls Batted":
                players_stats = batting_balls_batted(player_names=player_name_list, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_spin=only_spin_bool, against_pace=only_pace_bool, bowling_types=bowling_types, against_bowler=bowler_name, innings_number=innings_number)
                plot_summary = get_plot_summary('balls_batted', top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_runs, bowler_name, only_pace_bool, only_spin_bool, right_arm_pace_bool, left_arm_pace_bool, right_arm_wrist_spin_bool, right_arm_off_spin_bool, left_arm_orthodox_bool, left_arm_wrist_bool)
                draw_batting_plots(players_stats, 'balls_batted', plot_summary)
                
            elif stat_to_show == "Total Dot Balls":
                players_stats = batting_dot_balls_batted(player_names=player_name_list, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_spin=only_spin_bool, against_pace=only_pace_bool, bowling_types=bowling_types, against_bowler=bowler_name, innings_number=innings_number)
                plot_summary = get_plot_summary('dot_balls_batted', top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_runs, bowler_name, only_pace_bool, only_spin_bool, right_arm_pace_bool, left_arm_pace_bool, right_arm_wrist_spin_bool, right_arm_off_spin_bool, left_arm_orthodox_bool, left_arm_wrist_bool)
                draw_batting_plots(players_stats, 'dot_balls_batted', plot_summary)
            