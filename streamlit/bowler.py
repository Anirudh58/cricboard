# bread and butter
import numpy as np
import os
import pandas as pd
from pathlib import Path
import sys

# streamlit components
import streamlit as st

# plotting utils
from matplotlib import pyplot as plt 

# my lib
from src.insights import total_wickets, bowling_strike_rate, bowling_average, bowling_economy

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
def populate_tournaments(match_format):
    df_tournament = pd.read_csv(os.path.join(clean_data_path, "tournament.csv"))
    tournaments = np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])
    return tournaments

@st.cache
def populate_batters():
    df_player = pd.read_csv(os.path.join(clean_data_path, "player.csv"))
    batters = ["ALL"]
    batters.extend(sorted(np.array(df_player[~df_player['player_display_name'].isnull()]['player_name'])))
    return batters

def draw_batting_plots(stats, metric, plot_summary):
    """
    Utility function to draw the bowling plots
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
    
def get_plot_summary(metric, top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_balls, batsman_name, lh_bat_bool, rh_bat_bool):
    """
    Takes a bunch of inputs and generates a string that is used for plot titles
    """
    
    if metric=='wickets':
        plot_summary = "Total Wickets taken by players "    
    elif metric=='strike_rate':
        plot_summary = "Strike Rate of players " 
        # min runs threshold
        if top_n != 0:
            plot_summary += ("\nMin Balls: " + str(minimum_balls))
    elif metric=='average':
        plot_summary = "Average of players " 
        # min runs threshold
        if top_n != 0:
            plot_summary += ("\nMin Balls: " + str(minimum_balls))
    elif metric=='economy':
        plot_summary = "Economy Rate " 
    
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
    if batsman_name != 'ALL':
        plot_summary += ("\nAgainst batsman: " + bowler_name)
    # against bowling types (broad)
    if lh_bat_bool or rh_bat_bool:
        if lh_bat_bool:
            plot_summary += ("\nAgainst left hand bat")
        elif rh_bat_bool:
            plot_summary += ("\nAgainst right hand bat")
            
    return plot_summary

def main(match_format, session_state):
    st.title("Bowling Stats")
        
    # Dividing the entire layout into 3 sections in the ratio 1:1:1
    col1, col2, col3 = st.beta_columns((1, 1, 1))
    
    # INPUT SECTION
    
    with col1:
        player_name_list = st.multiselect("Choose player: (will be overriden when 'Top n' > 0) ", options=populate_players())
        years_range = st.slider("The period you want to consider:", min_value=2000, max_value=2021, value=(2000, 2021), step=1, format="%d")
        overs_range = st.slider("The overs range you want to consider: ", min_value=0, max_value=20, value=(0,20), step=1, format="%d")
        lh_bat_bool = st.checkbox("Against LH Bat")
        rh_bat_bool = st.checkbox("Against RH Bat")
    
    with col2:
        top_n = st.number_input("Top n performers (0 for single player stats): ", min_value=0, max_value=10, step=1, format="%d")
        venue = st.selectbox("Venue:", options=populate_venues())
        minimum_balls = st.number_input("Min balls bowled (for SR and Average): ", min_value=100, max_value=2000, step=1, format="%d")
        
    with col3:
        tournaments = st.multiselect("Tournaments:", options=populate_tournaments(match_format))        
        innings_number = st.number_input("Innnings number: (0 -> both) ", min_value=0, max_value=2, step=1, format="%d")
        batsman_name = st.selectbox("Against a specific batsman ", options=populate_batters())
        

    # OUTPUT SECTION
    
    col1, col2, col3, col4 = st.beta_columns((1, 1, 1, 1))
    
    batting_types = {
        "lh_bat_bool" : lh_bat_bool,
        "rh_bat_bool" : rh_bat_bool
    }
    
    if player_name_list or top_n > 0:
        with col1:
            
            players_stats = total_wickets(player_names=player_name_list, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_batsman=batsman_name, batting_types=batting_types, innings_number=innings_number)
            
            plot_summary = get_plot_summary('wickets', top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_balls, batsman_name, lh_bat_bool, rh_bat_bool)
            draw_batting_plots(players_stats, 'wickets', plot_summary)
            
            
            #st.header("Wickets")
            #st.table(total_wickets(player_name=player_name, top_n=top_n, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_batsman=batsman_name, batting_types=batting_types, innings_number=innings_number))

        with col2:
            
            players_stats = bowling_strike_rate(player_names=player_name_list, top_n=top_n, minimum_balls=minimum_balls, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_batsman=batsman_name, batting_types=batting_types, innings_number=innings_number)
            plot_summary = get_plot_summary('strike_rate', top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_balls, batsman_name, lh_bat_bool, rh_bat_bool)
            draw_batting_plots(players_stats, 'strike_rate', plot_summary)
            
            #st.header("Strike Rate")
            #st.table(bowling_strike_rate(player_name=player_name, top_n=top_n, minimum_balls=minimum_balls, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_batsman=batsman_name, batting_types=batting_types, innings_number=innings_number))


        with col3:
            
            players_stats = bowling_average(player_names=player_name_list, top_n=top_n, minimum_balls=minimum_balls, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_batsman=batsman_name, batting_types=batting_types, innings_number=innings_number)
            plot_summary = get_plot_summary('average', top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_balls, batsman_name, lh_bat_bool, rh_bat_bool)
            draw_batting_plots(players_stats, 'average', plot_summary)
            
            
            #st.header("Average")
            #st.table(bowling_average(player_name=player_name, top_n=top_n, minimum_balls=minimum_balls, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_batsman=batsman_name, batting_types=batting_types, innings_number=innings_number))


        with col4:
            
            players_stats = bowling_economy(player_names=player_name_list, top_n=top_n, minimum_balls=minimum_balls, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_batsman=batsman_name, batting_types=batting_types, innings_number=innings_number)
            plot_summary = get_plot_summary('economy', top_n, tournaments, venue, years_range, overs_range, innings_number, minimum_balls, batsman_name, lh_bat_bool, rh_bat_bool)
            draw_batting_plots(players_stats, 'economy', plot_summary)
                                     
            #st.header("Economy")
            #st.table(bowling_economy(player_name=player_name, top_n=top_n, minimum_balls=minimum_balls, match_format=match_format, tournaments=tournaments, venue_name=venue, years_range=years_range, overs_range=overs_range, against_batsman=batsman_name, batting_types=batting_types, innings_number=innings_number))


    