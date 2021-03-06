# Basic
from collections import Counter
import datetime
import math
import numpy as np
import os
import pprint

# yaml specific
import yaml

# Data handling
from fuzzywuzzy import fuzz, process
import pandas as pd
from tqdm import tqdm

# my library
from db_utils import update_player, add_player 

# Config variables
raw_data_path = "raw_data"
clean_data_path = "clean_data"
tournament_name = "IPL"

# Global utility maps

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

df_match = pd.read_csv(os.path.join(clean_data_path, "match.csv"))
df_match = df_match.loc[:, ~df_match.columns.str.contains('^Unnamed')]

df_ball = pd.read_csv(os.path.join(clean_data_path, "ball.csv"))
df_ball = df_ball.loc[:, ~df_ball.columns.str.contains('^Unnamed')]


def runs(player, tournaments=None, venue=None, years=None, overs_range=None, against_spin=None, against_pace=None, against_bowler=None):
    """
        Total runs for a player
        Args:
            player - (int) id of target player
            tournaments - (list of ints) list of tournament ids
            venue - (int) id of venue. 
            years - (list) list of years you want to consider
            overs_range - (list) 2 member list denoting [start_over, end_over]
            against_spin - (boolean) mark it true if you want data only specific to spin. dont mark this if you supply 'against_bowler'
            against_pace - (boolean) mark it true if you want data only specific to pace. dont mark this if you supply 'against_bowler'
            against_bowler - (int) id of specific bowler to find data against
    """
    
    # Grabbing all balls faced by this player
    required_balls = df_ball[df_ball["batsman"] == player]
    
    # Grabbing all matches to map ids
    required_matches = df_match
    
    # Run the required_matches dataframe through each match filter
    
    if tournaments is not None:
        #tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in tournaments.split(",")]
        required_matches = required_matches[required_matches['tournament_id'].isin(tournaments)]
        
    if venue is not None:
        required_matches = required_matches[required_matches['venue_id'] == venue]
        
    if years is not None:
        required_matches = required_matches[required_matches['match_date'].str.contains('|'.join(years))]
    
    match_ids_to_consider = np.array(required_matches['match_id'])
    required_balls = required_balls[required_balls['match_id'].isin(match_ids_to_consider)]
        
    if overs_range is not None:
        required_balls = required_balls[(required_balls['ball_number'] >= overs_range[0]) & (required_balls['ball_number'] <= overs_range[1])]
    
    if against_bowler is not None:
        required_balls = required_balls[required_balls['bowler'] == against_bowler]

    # TODO
    if against_spin is not None:
        only_spin = True
    
    # TODO
    if against_pace is not None:
        only_pace = True
    
    result = required_balls['batsman_runs'].sum()
        
    return result

def balls(player, tournaments=None, venue=None, years=None, overs_range=None, against_spin=None, against_pace=None, against_bowler=None):
    """
        Total balls played by a player given the conditions
        Args:
            player - (int) id of target player
            tournaments - (list of ints) list of tournament ids
            venue - (int) id of venue. 
            years - (list) list of years you want to consider
            overs_range - (list) 2 member list denoting [start_over, end_over]
            against_spin - (boolean) mark it true if you want data only specific to spin. dont mark this if you supply 'against_bowler'
            against_pace - (boolean) mark it true if you want data only specific to pace. dont mark this if you supply 'against_bowler'
            against_bowler - (int) id of specific bowler to find data against
    """
    
    # Grabbing all balls faced by this player
    required_balls = df_ball[df_ball["batsman"] == player]
    
    # Grabbing all matches to map ids
    required_matches = df_match
    
    # Run the required_matches dataframe through each match filter
    
    if tournaments is not None:
        #tournaments_to_consider = [tournament_id_map[tournament_name] for tournament_name in tournaments.split(",")]
        required_matches = required_matches[required_matches['tournament_id'].isin(tournaments)]
        
    if venue is not None:
        required_matches = required_matches[required_matches['venue_id'] == venue]
        
    if years is not None:
        required_matches = required_matches[required_matches['match_date'].str.contains('|'.join(years))]
    
    match_ids_to_consider = np.array(required_matches['match_id'])
    required_balls = required_balls[required_balls['match_id'].isin(match_ids_to_consider)]
        
    if overs_range is not None:
        required_balls = required_balls[(required_balls['ball_number'] >= overs_range[0]) & (required_balls['ball_number'] <= overs_range[1])]
    
    if against_bowler is not None:
        required_balls = required_balls[required_balls['bowler'] == against_bowler]

    # TODO
    if against_spin is not None:
        only_spin = True
    
    # TODO
    if against_pace is not None:
        only_pace = True
    
    result = len(required_balls)
        
    return result