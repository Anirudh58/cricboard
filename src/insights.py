import math
import numpy as np
import os
import pandas as pd
import streamlit as st

# batsman
from src.core import runs_scored, balls_batted, dismissals
# bowler
from src.core import wickets_taken, balls_bowled, runs_given


# GLOBAL CONSTANTS
INF = 100000000

# Set this to true when you are playing around with data in notebooks
DEBUG_MODE = False

# Config variables
if DEBUG_MODE:
    raw_data_path = os.path.join("..", "raw_data") 
    clean_data_path = os.path.join("..", "clean_data") 
else:
    raw_data_path = "raw_data"
    clean_data_path = "clean_data"

# Global variables

df_tournament = pd.read_csv(os.path.join(clean_data_path, "tournament.csv"))
df_tournament = df_tournament.loc[:, ~df_tournament.columns.str.contains('^Unnamed')]
tournament_id_map = dict(zip(df_tournament.tournament_name, df_tournament.tournament_id))

df_venue = pd.read_csv(os.path.join(clean_data_path, "venue.csv"))
df_venue = df_venue.loc[:, ~df_venue.columns.str.contains('^Unnamed')]
venue_id_map = dict(zip(df_venue.venue_name, df_venue.venue_id))

# Mapping the duplicates as well to its correct venue ids
venue_id_map["Punjab Cricket Association IS Bindra Stadium, Mohali"] = venue_id_map["Punjab Cricket Association Stadium, Mohali"]
venue_id_map["M.Chinnaswamy Stadium"] = venue_id_map["M Chinnaswamy Stadium"]

df_team = pd.read_csv(os.path.join(clean_data_path, "team.csv"))
df_team = df_team.loc[:, ~df_team.columns.str.contains('^Unnamed')]
team_id_map = dict(zip(df_team.team_name, df_team.team_id))

df_player = pd.read_csv(os.path.join(clean_data_path, "player.csv"))
df_player = df_player.loc[:, ~df_player.columns.str.contains('^Unnamed')]
player_dispname_id_map = dict(zip(df_player.player_display_name, df_player.player_id))
player_name_id_map = dict(zip(df_player.player_name, df_player.player_id))
player_id_name_map = dict(zip(df_player.player_id, df_player.player_name))


################################### BATSMAN INSIGHTS ###################################

# TODO: All time runs in IPL seems to have a minor discrepancy in our value and the value in IPL site. Check it later
@st.cache
def batting_total_runs(player_name, top_n, match_format, against_spin, against_pace, bowling_types, against_bowler, tournaments=None, venue_name=None, years_range=None, overs_range=None):
    """
        Total runs for a player / top runs
        Args:
            player_name - (string) the target player
            top_n - (int) if top_n is not 0, player_name will be overridden
            match_format - (string) one of 'ODI', 'TEST' or 'T20'
            bowling_types - (dict) a dictionary of boolean variables telling what bowling types you want the data for
            tournaments - (string) comma separated tournament codes eg: "IPL,BBL"
            venue_id - (integer) id of venue. 
            years_range - (list) 2 member list of start and end year
            overs_range - (string) should be in the format 'a-b'. eg: "0-6"
            against_spin - (boolean) mark it true if you want data only specific to spin. dont mark this if you supply 'against_bowler'
            against_pace - (boolean) mark it true if you want data only specific to pace. dont mark this if you supply 'against_bowler'
            against_bowler - (string) bowler name to find 1v1 data
    """
    
    if len(tournaments) > 0:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in tournaments]
    # if no tournament given, collect all tournament in this specified format
    else:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])]
    
    # Getting the venue id from the venue name
    venue_id_to_consider = None
    if venue_name != 'ALL':
        venue_id_to_consider = venue_id_map[venue_name]
    
    # defaults to full slider (all years)
    years_to_consider= [str(year) for year in range(years_range[0], years_range[1]+1)]
    
    # defaults to full slider (all overs)
    start_end_over_to_consider = [overs_range[0], overs_range[1]]    
    
    bowler_to_consider = 'ALL'
    if against_bowler != 'ALL':
        bowler_to_consider = player_name_id_map[against_bowler]
    
    # default value of top_n is 0, then just calculate for the given player name
    if top_n == 0:
        # Getting the player id from the name
        player_id_to_consider = player_name_id_map[player_name]
        result_runs = runs_scored(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
    
        result_columns = ["player_name", "runs"]
        df_result = pd.DataFrame(columns = result_columns)
        df_result = df_result.append({"player_name" : player_name, 
                                "runs" : result_runs}, ignore_index=True)
        
    else:
        players_stats = []
        top_counter = 0
        for player_i in player_dispname_id_map:
            # To avoid nan objects
            if isinstance(player_i, str):
                player_stat = {}
                player_id_to_consider = player_dispname_id_map[player_i]
                
                result_runs = runs_scored(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
                
                player_stat["player_name"] = player_id_name_map[player_id_to_consider]
                player_stat["runs"] = result_runs
                
                players_stats.append(player_stat)
        
        # sorting players based on runs
        top_players = sorted(players_stats, key = lambda player: player['runs'], reverse=True)
        
        result_columns = ["player_name", "runs"]
        df_result = pd.DataFrame(columns = result_columns)
        
        for i in range(top_n):
            df_result = df_result.append({"player_name" : top_players[i]["player_name"], 
                                            "runs" : top_players[i]["runs"]}, ignore_index=True)
        
    return df_result

@st.cache
def batting_strike_rate(player_name, top_n, match_format, against_spin, against_pace, bowling_types, against_bowler, minimum_runs, tournaments=None, venue_name=None, years_range=None, overs_range=None):
    """
        Strike rate for a player / top strike rates
        Args:
            player_name - (string) the target player
            top_n - (int) if top_n is not 0, player_name will be overridden
            match_format - (string) one of 'ODI', 'TEST' or 'T20'
            minimum_runs - (int) consider only those players who have crossed this threshold runs
            tournaments - (string) comma separated tournament codes eg: "IPL,BBL"
            venue_id - (integer) id of venue. 
            years_range - (list) 2 member list of start and end year
            overs_range - (string) should be in the format 'a-b'. eg: "0-6"
            against_spin - (boolean) mark it true if you want data only specific to spin. dont mark this if you supply 'against_bowler'
            against_pace - (boolean) mark it true if you want data only specific to pace. dont mark this if you supply 'against_bowler'
            against_bowler - (string) bowler name to find 1v1 data
    """
    
    if len(tournaments) > 0:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in tournaments]
    # if no tournament given, collect all tournament in this specified format
    else:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])]
    
    # Getting the venue id from the venue name
    venue_id_to_consider = None
    if venue_name != 'ALL':
        venue_id_to_consider = venue_id_map[venue_name]
    
    # defaults to full slider (all years)
    years_to_consider= [str(year) for year in range(years_range[0], years_range[1]+1)]
    
    # defaults to full slider (all overs)
    start_end_over_to_consider = [overs_range[0], overs_range[1]]    
    
    bowler_to_consider = 'ALL'
    if against_bowler != 'ALL':
        bowler_to_consider = player_name_id_map[against_bowler]
    
    # default value of top_n is 0, then just calculate for the given player name
    if top_n == 0:
        # Getting the player id from the name
        player_id_to_consider = player_name_id_map[player_name]
        result_runs = runs_scored(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
        
        result_balls = balls_batted(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
        
        result_columns = ["player_name", "strike_rate"]
        df_result = pd.DataFrame(columns = result_columns)
        
        if result_balls == 0:
            result_strike_rate = INF
        else:
            result_strike_rate = np.float64(result_runs/np.float64(result_balls)) * 100
            
        df_result = df_result.append({"player_name" : player_name, 
                                "strike_rate" : result_strike_rate}, ignore_index=True)
        
    else:
        player_stats = []
        top_counter = 0
        for player_i in player_dispname_id_map:
            # To avoid nan objects
            if isinstance(player_i, str):
                player_stat = {}
                player_id_to_consider = player_dispname_id_map[player_i]
                
                result_runs = runs_scored(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
                
                result_balls = balls_batted(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
                
                if result_balls == 0:
                    result_strike_rate = INF
                else:
                    result_strike_rate = np.float64(result_runs/np.float64(result_balls)) * 100
                
                player_stat["player_name"] = player_id_name_map[player_id_to_consider]
                player_stat["strike_rate"] = result_strike_rate
                
                if result_runs > minimum_runs:
                    player_stats.append(player_stat)
        
        # sorting players based on runs
        top_players = sorted(player_stats, key = lambda player: player['strike_rate'], reverse=True)
        
        result_columns = ["player_name", "strike_rate"]
        df_result = pd.DataFrame(columns = result_columns)
        
        for i in range(min(top_n, len(player_stats))):
            df_result = df_result.append({"player_name" : top_players[i]["player_name"], 
                                            "strike_rate" : top_players[i]["strike_rate"]}, ignore_index=True)
        
    return df_result

@st.cache
def batting_average(player_name, top_n, match_format, against_spin, against_pace, bowling_types, against_bowler, minimum_runs, tournaments=None, venue_name=None, years_range=None, overs_range=None):
    """
        Average for a player / top averages
        Args:
            player_name - (string) the target player
            top_n - (int) if top_n is not 0, player_name will be overridden
            match_format - (string) one of 'ODI', 'TEST' or 'T20'
            minimum_runs - (int) consider only those players who have crossed this threshold runs
            tournaments - (string) comma separated tournament codes eg: "IPL,BBL"
            venue_id - (integer) id of venue. 
            years_range - (list) 2 member list of start and end year
            overs_range - (string) should be in the format 'a-b'. eg: "0-6"
            against_spin - (boolean) mark it true if you want data only specific to spin. dont mark this if you supply 'against_bowler'
            against_pace - (boolean) mark it true if you want data only specific to pace. dont mark this if you supply 'against_bowler'
            against_bowler - (string) bowler name to find 1v1 data
    """
    
    if len(tournaments) > 0:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in tournaments]
    # if no tournament given, collect all tournament in this specified format
    else:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])]
    
    # Getting the venue id from the venue name
    venue_id_to_consider = None
    if venue_name != 'ALL':
        venue_id_to_consider = venue_id_map[venue_name]
    
    # defaults to full slider (all years)
    years_to_consider= [str(year) for year in range(years_range[0], years_range[1]+1)]
    
    # defaults to full slider (all overs)
    start_end_over_to_consider = [overs_range[0], overs_range[1]]    
    
    bowler_to_consider = 'ALL'
    if against_bowler != 'ALL':
        bowler_to_consider = player_name_id_map[against_bowler]
    
    # default value of top_n is 0, then just calculate for the given player name
    if top_n == 0:
        # Getting the player id from the name
        player_id_to_consider = player_name_id_map[player_name]
        result_runs = runs_scored(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
        
        result_dismissals = dismissals(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
        
        if result_dismissals == 0:
            result_average = INF
        else:
            result_average = np.float64(result_runs/np.float64(result_dismissals))
        
        result_columns = ["player_name", "average"]
        df_result = pd.DataFrame(columns = result_columns)
        df_result = df_result.append({"player_name" : player_name, 
                                "average" : result_average}, ignore_index=True)
        
    else:
        player_stats = []
        top_counter = 0
        for player_i in player_dispname_id_map:
            # To avoid nan objects
            if isinstance(player_i, str):
                player_stat = {}
                player_id_to_consider = player_dispname_id_map[player_i]
                
                result_runs = runs_scored(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
                
                result_dismissals = dismissals(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
                
                if result_dismissals == 0:
                    result_average = INF
                else:
                    result_average = np.float64(result_runs/np.float64(result_dismissals))
                
                player_stat["player_name"] = player_id_name_map[player_id_to_consider]
                player_stat["average"] = result_average
                
                if result_runs > minimum_runs:
                    player_stats.append(player_stat)
        
        # sorting players based on runs
        top_players = sorted(player_stats, key = lambda player: player['average'], reverse=True)
        
        result_columns = ["player_name", "average"]
        df_result = pd.DataFrame(columns = result_columns)
        
        for i in range(min(top_n, len(player_stats))):
            df_result = df_result.append({"player_name" : top_players[i]["player_name"], 
                                            "average" : top_players[i]["average"]}, ignore_index=True)
        
    return df_result


@st.cache
def batting_dismissals(player_name, top_n, match_format, against_spin, against_pace, bowling_types, against_bowler, tournaments=None, venue_name=None, years_range=None, overs_range=None):
    """
        Average for a player / top averages
        Args:
            player_name - (string) the target player
            top_n - (int) if top_n is not 0, player_name will be overridden
            match_format - (string) one of 'ODI', 'TEST' or 'T20'
            minimum_runs - (int) consider only those players who have crossed this threshold runs
            tournaments - (string) comma separated tournament codes eg: "IPL,BBL"
            venue_id - (integer) id of venue. 
            years_range - (list) 2 member list of start and end year
            overs_range - (string) should be in the format 'a-b'. eg: "0-6"
            against_spin - (boolean) mark it true if you want data only specific to spin. dont mark this if you supply 'against_bowler'
            against_pace - (boolean) mark it true if you want data only specific to pace. dont mark this if you supply 'against_bowler'
            against_bowler - (string) bowler name to find 1v1 data
    """
    
    if len(tournaments) > 0:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in tournaments]
    # if no tournament given, collect all tournament in this specified format
    else:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])]
    
    # Getting the venue id from the venue name
    venue_id_to_consider = None
    if venue_name != 'ALL':
        venue_id_to_consider = venue_id_map[venue_name]
    
    # defaults to full slider (all years)
    years_to_consider= [str(year) for year in range(years_range[0], years_range[1]+1)]
    
    # defaults to full slider (all overs)
    start_end_over_to_consider = [overs_range[0], overs_range[1]]    
    
    bowler_to_consider = 'ALL'
    if against_bowler != 'ALL':
        bowler_to_consider = player_name_id_map[against_bowler]
    
    # default value of top_n is 0, then just calculate for the given player name
    if top_n == 0:
        # Getting the player id from the name
        player_id_to_consider = player_name_id_map[player_name]
        
        result_dismissals = dismissals(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
        
        
        result_columns = ["player_name", "dismissals"]
        df_result = pd.DataFrame(columns = result_columns)
        df_result = df_result.append({"player_name" : player_name, 
                                "dismissals" : result_dismissals}, ignore_index=True)
        
    else:
        player_stats = []
        top_counter = 0
        for player_i in player_dispname_id_map:
            # To avoid nan objects
            if isinstance(player_i, str):
                player_stat = {}
                player_id_to_consider = player_dispname_id_map[player_i]
                
                result_dismissals = dismissals(player=player_id_to_consider, against_spin=against_spin, against_pace=against_pace, bowling_types=bowling_types, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_bowler=bowler_to_consider)
                
                player_stat["player_name"] = player_id_name_map[player_id_to_consider]
                player_stat["dismissals"] = result_dismissals
                
                player_stats.append(player_stat)
        
        # sorting players based on dismissals
        top_players = sorted(player_stats, key = lambda player: player['dismissals'], reverse=True)
        
        result_columns = ["player_name", "dismissals"]
        df_result = pd.DataFrame(columns = result_columns)
        
        for i in range(min(top_n, len(player_stats))):
            df_result = df_result.append({"player_name" : top_players[i]["player_name"], 
                                            "dismissals" : top_players[i]["dismissals"]}, ignore_index=True)
        
    return df_result

    
################################### END BATSMAN INSIGHTS ###################################


################################### BOWLER INSIGHTS ###################################

@st.cache
def total_wickets(player_name, top_n, match_format, against_batsman, batting_types, tournaments=None, venue_name=None, years_range=None, overs_range=None):
    """
        Total wickets taken by a player / top wicket takers
        Args:
            player_name - (string) the target player
            top_n - (int) if top_n is not 0, player_name will be overridden
            match_format - (string) one of 'ODI', 'TEST' or 'T20'
            against_batsman - (string) name of batsman to show stats against
            batting_types - (dict) dict of lhb and rhb denoting users option
            tournaments - (string) comma separated tournament codes eg: "IPL,BBL"
            venue_name - (string) name of venue. 
            years_range - (list) 2 member list of start and end year
            overs_range - (string) should be in the format 'a-b'. eg: "0-6"
    """
    
    if len(tournaments) > 0:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in tournaments]
    # if no tournament given, collect all tournament in this specified format
    else:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])]
    
    # Getting the venue id from the venue name
    venue_id_to_consider = None
    if venue_name != 'ALL':
        venue_id_to_consider = venue_id_map[venue_name]
    
    # defaults to full slider (all years)
    years_to_consider= [str(year) for year in range(years_range[0], years_range[1]+1)]
    
    # defaults to full slider (all overs)
    start_end_over_to_consider = [overs_range[0], overs_range[1]]    
    
    batter_to_consider = 'ALL'
    if against_batsman != 'ALL':
        batter_to_consider = player_name_id_map[against_batsman]
    
    # default value of top_n is 0, then just calculate for the given player name
    if top_n == 0:
        # Getting the player id from the name
        player_id_to_consider = player_name_id_map[player_name]
        result_wickets = wickets_taken(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
    
        result_columns = ["player_name", "wickets"]
        df_result = pd.DataFrame(columns = result_columns)
        df_result = df_result.append({"player_name" : player_name, 
                                "wickets" : result_wickets}, ignore_index=True)
        
    else:
        players_stats = []
        top_counter = 0
        for player_i in player_dispname_id_map:
            # To avoid nan objects
            if isinstance(player_i, str):
                players_stat = {}
                player_id_to_consider = player_dispname_id_map[player_i]
                
                result_wickets = wickets_taken(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
                
                players_stat["player_name"] = player_id_name_map[player_id_to_consider]
                players_stat["wickets"] = result_wickets
                
                players_stats.append(players_stat)
        
        # sorting players based on wickets
        top_players = sorted(players_stats, key = lambda player: player['wickets'], reverse=True)
        
        result_columns = ["player_name", "wickets"]
        df_result = pd.DataFrame(columns = result_columns)
        
        for i in range(top_n):
            df_result = df_result.append({"player_name" : top_players[i]["player_name"], 
                                            "wickets" : top_players[i]["wickets"]}, ignore_index=True)
        
    return df_result

@st.cache
def bowling_strike_rate(player_name, top_n, minimum_balls, match_format, against_batsman, batting_types, tournaments=None, venue_name=None, years_range=None, overs_range=None):
    """
        Total wickets taken by a player / top wicket takers
        Args:
            player_name - (string) the target player
            top_n - (int) if top_n is not 0, player_name will be overridden
            minimum_balls - (int) threshold
            match_format - (string) one of 'ODI', 'TEST' or 'T20'
            against_batsman - (string) name of batsman to show stats against
            batting_types - (dict) dict of lhb and rhb denoting users option
            tournaments - (string) comma separated tournament codes eg: "IPL,BBL"
            venue_name - (string) name of venue. 
            years_range - (list) 2 member list of start and end year
            overs_range - (string) should be in the format 'a-b'. eg: "0-6"
    """
    
    if len(tournaments) > 0:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in tournaments]
    # if no tournament given, collect all tournament in this specified format
    else:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])]
    
    # Getting the venue id from the venue name
    venue_id_to_consider = None
    if venue_name != 'ALL':
        venue_id_to_consider = venue_id_map[venue_name]
    
    # defaults to full slider (all years)
    years_to_consider= [str(year) for year in range(years_range[0], years_range[1]+1)]
    
    # defaults to full slider (all overs)
    start_end_over_to_consider = [overs_range[0], overs_range[1]]    
    
    batter_to_consider = 'ALL'
    if against_batsman != 'ALL':
        batter_to_consider = player_name_id_map[against_batsman]
    
    # default value of top_n is 0, then just calculate for the given player name
    if top_n == 0:
        # Getting the player id from the name
        player_id_to_consider = player_name_id_map[player_name]
        result_wickets = wickets_taken(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
        
        result_balls = balls_bowled(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
        
        if result_wickets == 0:
            result_strike_rate = INF
        else:
            result_strike_rate = np.float64(result_balls/np.float64(result_wickets))
    
        result_columns = ["player_name", "strike_rate"]
        df_result = pd.DataFrame(columns = result_columns)
        df_result = df_result.append({"player_name" : player_name, 
                                "strike_rate" : result_strike_rate}, ignore_index=True)
        
    else:
        player_stats = []
        top_counter = 0
        for player_i in player_dispname_id_map:
            # To avoid nan objects
            if isinstance(player_i, str):
                player_stat = {}
                player_id_to_consider = player_dispname_id_map[player_i]
                
                result_wickets = wickets_taken(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
                
                result_balls = balls_bowled(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
                
                if result_wickets == 0:
                    result_strike_rate = INF
                else:
                    result_strike_rate = np.float64(result_balls/np.float64(result_wickets))
                
                player_stat["player_name"] = player_id_name_map[player_id_to_consider]
                player_stat["strike_rate"] = result_strike_rate
                
                if result_balls > minimum_balls:
                    player_stats.append(player_stat)
        
        # sorting players based on wickets
        top_players = sorted(player_stats, key = lambda player: player['strike_rate'], reverse=False)
        
        result_columns = ["player_name", "strike_rate"]
        df_result = pd.DataFrame(columns = result_columns)
        
        for i in range(min(top_n, len(player_stats))):
            df_result = df_result.append({"player_name" : top_players[i]["player_name"], 
                                            "strike_rate" : top_players[i]["strike_rate"]}, ignore_index=True)
        
    return df_result


@st.cache
def bowling_average(player_name, top_n, minimum_balls, match_format, against_batsman, batting_types, tournaments=None, venue_name=None, years_range=None, overs_range=None):
    """
        Total wickets taken by a player / top wicket takers
        Args:
            player_name - (string) the target player
            top_n - (int) if top_n is not 0, player_name will be overridden
            minimum_balls - (int) threshold
            match_format - (string) one of 'ODI', 'TEST' or 'T20'
            against_batsman - (string) name of batsman to show stats against
            batting_types - (dict) dict of lhb and rhb denoting users option
            tournaments - (string) comma separated tournament codes eg: "IPL,BBL"
            venue_name - (string) name of venue. 
            years_range - (list) 2 member list of start and end year
            overs_range - (string) should be in the format 'a-b'. eg: "0-6"
    """
    
    
    if len(tournaments) > 0:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in tournaments]
    # if no tournament given, collect all tournament in this specified format
    else:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])]
    
    # Getting the venue id from the venue name
    venue_id_to_consider = None
    if venue_name != 'ALL':
        venue_id_to_consider = venue_id_map[venue_name]
    
    # defaults to full slider (all years)
    years_to_consider= [str(year) for year in range(years_range[0], years_range[1]+1)]
    
    # defaults to full slider (all overs)
    start_end_over_to_consider = [overs_range[0], overs_range[1]]    
    
    batter_to_consider = 'ALL'
    if against_batsman != 'ALL':
        batter_to_consider = player_name_id_map[against_batsman]
    
    # default value of top_n is 0, then just calculate for the given player name
    if top_n == 0:
        # Getting the player id from the name
        player_id_to_consider = player_name_id_map[player_name]
        result_wickets = wickets_taken(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
        
        result_runs = runs_given(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
        
        if result_wickets == 0:
            result_average = INF
        else:
            result_average = np.float64(result_runs/np.float64(result_wickets))
    
        result_columns = ["player_name", "average"]
        df_result = pd.DataFrame(columns = result_columns)
        df_result = df_result.append({"player_name" : player_name, 
                                "average" : result_average}, ignore_index=True)
        
    else:
        player_stats = []
        top_counter = 0
        for player_i in player_dispname_id_map:
            # To avoid nan objects
            if isinstance(player_i, str):
                player_stat = {}
                player_id_to_consider = player_dispname_id_map[player_i]
                
                result_wickets = wickets_taken(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
                
                result_runs = runs_given(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
                
                result_balls = balls_bowled(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
                
                if result_wickets == 0:
                    result_average = INF
                else:
                    result_average = np.float64(result_runs/np.float64(result_wickets))
                
                player_stat["player_name"] = player_id_name_map[player_id_to_consider]
                player_stat["average"] = result_average
                
                if result_balls > minimum_balls:
                    player_stats.append(player_stat)
        
        # sorting players based on wickets
        top_players = sorted(player_stats, key = lambda player: player['average'], reverse=False)
        
        result_columns = ["player_name", "average"]
        df_result = pd.DataFrame(columns = result_columns)
        
        for i in range(min(top_n, len(player_stats))):
            df_result = df_result.append({"player_name" : top_players[i]["player_name"], 
                                            "average" : top_players[i]["average"]}, ignore_index=True)
        
    return df_result


@st.cache
def bowling_economy(player_name, top_n, minimum_balls, match_format, against_batsman, batting_types, tournaments=None, venue_name=None, years_range=None, overs_range=None):
    """
        Total wickets taken by a player / top wicket takers
        Args:
            player_name - (string) the target player
            top_n - (int) if top_n is not 0, player_name will be overridden
            minimum_balls - (int) threshold
            match_format - (string) one of 'ODI', 'TEST' or 'T20'
            against_batsman - (string) name of batsman to show stats against
            batting_types - (dict) dict of lhb and rhb denoting users option
            tournaments - (string) comma separated tournament codes eg: "IPL,BBL"
            venue_name - (string) name of venue. 
            years_range - (list) 2 member list of start and end year
            overs_range - (string) should be in the format 'a-b'. eg: "0-6"
    """
    
    
    if len(tournaments) > 0:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in tournaments]
    # if no tournament given, collect all tournament in this specified format
    else:
        tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in np.array(df_tournament[df_tournament["tournament_format"] == match_format]["tournament_name"])]
    
    # Getting the venue id from the venue name
    venue_id_to_consider = None
    if venue_name != 'ALL':
        venue_id_to_consider = venue_id_map[venue_name]
    
    # defaults to full slider (all years)
    years_to_consider= [str(year) for year in range(years_range[0], years_range[1]+1)]
    
    # defaults to full slider (all overs)
    start_end_over_to_consider = [overs_range[0], overs_range[1]]    
    
    batter_to_consider = 'ALL'
    if against_batsman != 'ALL':
        batter_to_consider = player_name_id_map[against_batsman]
    
    # default value of top_n is 0, then just calculate for the given player name
    if top_n == 0:
        # Getting the player id from the name
        player_id_to_consider = player_name_id_map[player_name]
        result_balls = balls_bowled(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
        
        result_runs = runs_given(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
        
        if result_balls == 0:
            result_economy = INF
        else:
            result_economy = np.float64(result_runs/np.float64(result_balls)) * 6.0
    
        result_columns = ["player_name", "economy"]
        df_result = pd.DataFrame(columns = result_columns)
        df_result = df_result.append({"player_name" : player_name, 
                                "economy" : result_economy}, ignore_index=True)
        
    else:
        player_stats = []
        top_counter = 0
        for player_i in player_dispname_id_map:
            # To avoid nan objects
            if isinstance(player_i, str):
                player_stat = {}
                player_id_to_consider = player_dispname_id_map[player_i]
                
                result_balls = balls_bowled(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
        
                result_runs = runs_given(player=player_id_to_consider, tournaments=tournaments_to_consider, venue=venue_id_to_consider, years=years_to_consider, overs_range=start_end_over_to_consider, against_batsman=batter_to_consider, batting_types=batting_types)
                
                if result_balls == 0:
                    result_economy = INF
                else:
                    result_economy = np.float64(result_runs/np.float64(result_balls)) * 6.0
                
                player_stat["player_name"] = player_id_name_map[player_id_to_consider]
                player_stat["economy"] = result_economy
                
                if result_balls > minimum_balls:
                    player_stats.append(player_stat)
        
        # sorting players based on wickets
        top_players = sorted(player_stats, key = lambda player: player['economy'], reverse=False)
        
        result_columns = ["player_name", "economy"]
        df_result = pd.DataFrame(columns = result_columns)
        
        for i in range(min(top_n, len(player_stats))):
            df_result = df_result.append({"player_name" : top_players[i]["player_name"], 
                                            "economy" : top_players[i]["economy"]}, ignore_index=True)
        
    return df_result


################################### END BOWLER INSIGHTS ###################################
