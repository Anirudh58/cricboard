#new branch
# Basic
from collections import Counter
import datetime
import inspect
import math
import numpy as np
import os
import pickle
import pprint

# yaml specific
import yaml

# Data handling
from fuzzywuzzy import fuzz, process
import pandas as pd
from tqdm import tqdm


# my library
from src.db_utils import update_player, add_player 

# Config variables
#raw_data_path = os.path.join("..", "raw_data") 
#clean_data_path = os.path.join("..", "clean_data") 

raw_data_path = "raw_data"
clean_data_path = "clean_data"

################################ GLOBAL UTILITY FUNCTIONS #######################################

def strip_special_chars(s):
    bad_chars = ["[", "]", "'"]
    for i in bad_chars:
        s = s.replace(i, '')
    return s

################################ GLOBAL UTILITY MAPS #######################################

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
match_id_date_map = {}
for index, row in df_match.iterrows():
    date_string = strip_special_chars(row['match_date'].split(',')[0])
    date_obj = datetime.date(*map(int, date_string.split('-')))
    match_id = row['match_id']
    match_id_date_map[match_id] = date_obj

df_ball = pd.read_csv(os.path.join(clean_data_path, "ball.csv"))
df_ball = df_ball.loc[:, ~df_ball.columns.str.contains('^Unnamed')]

with open(os.path.join(clean_data_path, 'fantasy.pkl'), 'rb') as fantasy_pi:
    fantasy_obj = pickle.load(fantasy_pi)

################################ BOWLER TYPE #######################################
    
# PLAYER IDS FOR PARTICULAR BOWLING TYPE

right_arm_pace_bowler_ID=list(df_player.loc[df_player['bowling_style']=='Right arm Pace','player_id'])
right_arm_wrist_spin_bowler_ID=list(df_player.loc[df_player['bowling_style']=='Right arm wrist spin','player_id'])
right_arm_off_spin_bowler_ID=list(df_player.loc[df_player['bowling_style']=='Right arm Off spin','player_id'])
left_arm_pace_bowler_ID=list(df_player.loc[df_player['bowling_style']=='Left arm Pace','player_id'])
left_arm_orthodox_bowler_ID=list(df_player.loc[df_player['bowling_style']=='Left arm Orthodox','player_id'])
left_arm_wrist_bowler_ID=list(df_player.loc[df_player['bowling_style']=='Left arm wrist','player_id'])
pace_bowler_ID = right_arm_pace_bowler_ID + left_arm_pace_bowler_ID 
spin_bowler_ID =  right_arm_wrist_spin_bowler_ID + right_arm_off_spin_bowler_ID + left_arm_orthodox_bowler_ID + left_arm_wrist_bowler_ID

################################ BATTER TYPES #######################################
    
# PLAYER IDS FOR PARTICULAR BATTING TYPE

lhb_ID = list(df_player.loc[df_player['batting_style']=='Left-hand bat','player_id'])
rhb_ID = list(df_player.loc[df_player['batting_style']=='Right-hand bat','player_id'])

################################### BATSMAN CORE ###################################

def runs_scored(player, against_spin, against_pace, bowling_types, against_bowler, innings_number, tournaments=None, venue=None, years=None, overs_range=None):
    """
        Total runs for a player given the conditions
        Args:
            player - (int) id of target player
            tournaments - (list of ints) list of tournament ids
            venue - (int) id of venue. 
            years - (list) list of years you want to consider
            overs_range - (list) 2 member list denoting [start_over, end_over]
            against_spin - (boolean) mark it true if you want data only specific to spin. dont mark this if you supply 'against_bowler'
            against_pace - (boolean) mark it true if you want data only specific to pace. dont mark this if you supply 'against_bowler'
            bowling_types - (dict) a dictionary of boolean variables telling what bowling types you want the data for
            against_bowler - (int) id of specific bowler to find data against
            innings_number - (int) - 1 -> batting first 2 -> batting second 0 -> both
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
        
    if innings_number != 0:
        required_balls = required_balls[required_balls['innings_number'] == innings_number]
    
    if against_bowler != 'ALL':
        required_balls = required_balls[required_balls['bowler'] == against_bowler]
    
    if against_spin:
        required_balls = required_balls[required_balls['bowler'].isin(spin_bowler_ID)]
    
    if against_pace:
        required_balls = required_balls[required_balls['bowler'].isin(pace_bowler_ID)]
        
    # This section will be executed only if user has clicked any of the checkbox for bowling types
    if ~against_spin and ~against_pace and any(bool_value for key, bool_value in bowling_types.items()):
        
        # Creating empty dataframes for the balls bowled by different bowling types
        right_arm_pace_required_balls = pd.DataFrame(columns=required_balls.columns)
        right_arm_wrist_spin_required_balls = pd.DataFrame(columns=required_balls.columns)
        right_arm_off_spin_required_balls = pd.DataFrame(columns=required_balls.columns)
        
        left_arm_pace_required_balls = pd.DataFrame(columns=required_balls.columns)
        left_arm_orthodox_required_balls = pd.DataFrame(columns=required_balls.columns)
        left_arm_wrist_required_balls = pd.DataFrame(columns=required_balls.columns)
        
        if bowling_types["right_arm_pace_bool"]:
            right_arm_pace_required_balls = required_balls[required_balls['bowler'].isin(right_arm_pace_bowler_ID)]
        
        if bowling_types["right_arm_wrist_spin_bool"]:
            right_arm_wrist_spin_required_balls = required_balls[required_balls['bowler'].isin(right_arm_wrist_spin_bowler_ID)]
            
        if bowling_types["right_arm_off_spin_bool"]:
            right_arm_off_spin_required_balls = required_balls[required_balls['bowler'].isin(right_arm_off_spin_bowler_ID)]
            
        if bowling_types["left_arm_pace_bool"]:
            left_arm_pace_required_balls = required_balls[required_balls['bowler'].isin(left_arm_pace_bowler_ID)]
            
        if bowling_types["left_arm_orthodox_bool"]:
            left_arm_orthodox_required_balls = required_balls[required_balls['bowler'].isin(left_arm_orthodox_bowler_ID)]
            
        if bowling_types["left_arm_wrist_bool"]:
            left_arm_wrist_required_balls = required_balls[required_balls['bowler'].isin(left_arm_wrist_bowler_ID)]
            
        # pd.concat defaults to an "outer" merge (UNION)
        required_balls = pd.concat([right_arm_pace_required_balls, right_arm_wrist_spin_required_balls, right_arm_off_spin_required_balls, left_arm_pace_required_balls,
                                   left_arm_orthodox_required_balls, left_arm_wrist_required_balls])
        
    result = required_balls['batsman_runs'].sum()
        
    return result

def balls_batted(player, against_spin, against_pace, bowling_types, against_bowler, innings_number, tournaments=None, venue=None, years=None, overs_range=None):
    """
        Total runs for a player given the conditions
        Args:
            player - (int) id of target player
            tournaments - (list of ints) list of tournament ids
            venue - (int) id of venue. 
            years - (list) list of years you want to consider
            overs_range - (list) 2 member list denoting [start_over, end_over]
            against_spin - (boolean) mark it true if you want data only specific to spin. dont mark this if you supply 'against_bowler'
            against_pace - (boolean) mark it true if you want data only specific to pace. dont mark this if you supply 'against_bowler'
            bowling_types - (dict) a dictionary of boolean variables telling what bowling types you want the data for
            against_bowler - (int) id of specific bowler to find data against
            innings_number - (int) - 1 -> batting first 2 -> batting second 0 -> both
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
        
    if innings_number != 0:
        required_balls = required_balls[required_balls['innings_number'] == innings_number]
    
    if against_bowler != 'ALL':
        required_balls = required_balls[required_balls['bowler'] == against_bowler]
    
    if against_spin:
        required_balls = required_balls[required_balls['bowler'].isin(spin_bowler_ID)]
    
    if against_pace:
        required_balls = required_balls[required_balls['bowler'].isin(pace_bowler_ID)]
        
    # This section will be executed only if user has clicked any of the checkbox for bowling types
    if ~against_spin and ~against_pace and any(bool_value for key, bool_value in bowling_types.items()):
        
        # Creating empty dataframes for the balls bowled by different bowling types
        right_arm_pace_required_balls = pd.DataFrame(columns=required_balls.columns)
        right_arm_wrist_spin_required_balls = pd.DataFrame(columns=required_balls.columns)
        right_arm_off_spin_required_balls = pd.DataFrame(columns=required_balls.columns)
        
        left_arm_pace_required_balls = pd.DataFrame(columns=required_balls.columns)
        left_arm_orthodox_required_balls = pd.DataFrame(columns=required_balls.columns)
        left_arm_wrist_required_balls = pd.DataFrame(columns=required_balls.columns)
        
        if bowling_types["right_arm_pace_bool"]:
            right_arm_pace_required_balls = required_balls[required_balls['bowler'].isin(right_arm_pace_bowler_ID)]
        
        if bowling_types["right_arm_wrist_spin_bool"]:
            right_arm_wrist_spin_required_balls = required_balls[required_balls['bowler'].isin(right_arm_wrist_spin_bowler_ID)]
            
        if bowling_types["right_arm_off_spin_bool"]:
            right_arm_off_spin_required_balls = required_balls[required_balls['bowler'].isin(right_arm_off_spin_bowler_ID)]
            
        if bowling_types["left_arm_pace_bool"]:
            left_arm_pace_required_balls = required_balls[required_balls['bowler'].isin(left_arm_pace_bowler_ID)]
            
        if bowling_types["left_arm_orthodox_bool"]:
            left_arm_orthodox_required_balls = required_balls[required_balls['bowler'].isin(left_arm_orthodox_bowler_ID)]
            
        if bowling_types["left_arm_wrist_bool"]:
            left_arm_wrist_required_balls = required_balls[required_balls['bowler'].isin(left_arm_wrist_bowler_ID)]
            
        # pd.concat defaults to an "outer" merge (UNION)
        required_balls = pd.concat([right_arm_pace_required_balls, right_arm_wrist_spin_required_balls, right_arm_off_spin_required_balls, left_arm_pace_required_balls,
                                   left_arm_orthodox_required_balls, left_arm_wrist_required_balls])
    
    result = len(required_balls)
        
    return result


def dismissals(player, against_spin, against_pace, bowling_types, against_bowler, innings_number, tournaments=None, venue=None, years=None, overs_range=None):
    """
        Total runs for a player given the conditions
        Args:
            player - (int) id of target player
            tournaments - (list of ints) list of tournament ids
            venue - (int) id of venue. 
            years - (list) list of years you want to consider
            overs_range - (list) 2 member list denoting [start_over, end_over]
            against_spin - (boolean) mark it true if you want data only specific to spin. dont mark this if you supply 'against_bowler'
            against_pace - (boolean) mark it true if you want data only specific to pace. dont mark this if you supply 'against_bowler'
            bowling_types - (dict) a dictionary of boolean variables telling what bowling types you want the data for
            against_bowler - (int) id of specific bowler to find data against
            innings_number - (int) - 1 -> batting first 2 -> batting second 0 -> both
    """
    
    # Grabbing all balls faced by this player
    required_balls = df_ball[(df_ball["batsman"] == player) | (df_ball["non_striker"] == player)]
    
    # Grabbing all matches to map ids
    required_matches = df_match
    
    # Run the required_matches dataframe through each match filter
    
    if tournaments is not None:
        required_matches = required_matches[required_matches['tournament_id'].isin(tournaments)]
        
    if venue is not None:
        required_matches = required_matches[required_matches['venue_id'] == venue]
        
    if years is not None:
        required_matches = required_matches[required_matches['match_date'].str.contains('|'.join(years))]
    
    match_ids_to_consider = np.array(required_matches['match_id'])
    required_balls = required_balls[required_balls['match_id'].isin(match_ids_to_consider)]
        
    if overs_range is not None:
        required_balls = required_balls[(required_balls['ball_number'] >= overs_range[0]) & (required_balls['ball_number'] <= overs_range[1])]
        
    if innings_number != 0:
        required_balls = required_balls[required_balls['innings_number'] == innings_number]
    
    if against_bowler != 'ALL':
        required_balls = required_balls[required_balls['bowler'] == against_bowler]
    
    if against_spin:
        required_balls = required_balls[required_balls['bowler'].isin(spin_bowler_ID)]
    
    if against_pace:
        required_balls = required_balls[required_balls['bowler'].isin(pace_bowler_ID)]
        
    # This section will be executed only if user has clicked any of the checkbox for bowling types
    if ~against_spin and ~against_pace and any(bool_value for key, bool_value in bowling_types.items()):
        
        # Creating empty dataframes for the balls bowled by different bowling types
        right_arm_pace_required_balls = pd.DataFrame(columns=required_balls.columns)
        right_arm_wrist_spin_required_balls = pd.DataFrame(columns=required_balls.columns)
        right_arm_off_spin_required_balls = pd.DataFrame(columns=required_balls.columns)
        
        left_arm_pace_required_balls = pd.DataFrame(columns=required_balls.columns)
        left_arm_orthodox_required_balls = pd.DataFrame(columns=required_balls.columns)
        left_arm_wrist_required_balls = pd.DataFrame(columns=required_balls.columns)
        
        if bowling_types["right_arm_pace_bool"]:
            right_arm_pace_required_balls = required_balls[required_balls['bowler'].isin(right_arm_pace_bowler_ID)]
        
        if bowling_types["right_arm_wrist_spin_bool"]:
            right_arm_wrist_spin_required_balls = required_balls[required_balls['bowler'].isin(right_arm_wrist_spin_bowler_ID)]
            
        if bowling_types["right_arm_off_spin_bool"]:
            right_arm_off_spin_required_balls = required_balls[required_balls['bowler'].isin(right_arm_off_spin_bowler_ID)]
            
        if bowling_types["left_arm_pace_bool"]:
            left_arm_pace_required_balls = required_balls[required_balls['bowler'].isin(left_arm_pace_bowler_ID)]
            
        if bowling_types["left_arm_orthodox_bool"]:
            left_arm_orthodox_required_balls = required_balls[required_balls['bowler'].isin(left_arm_orthodox_bowler_ID)]
            
        if bowling_types["left_arm_wrist_bool"]:
            left_arm_wrist_required_balls = required_balls[required_balls['bowler'].isin(left_arm_wrist_bowler_ID)]
            
        # pd.concat defaults to an "outer" merge (UNION)
        required_balls = pd.concat([right_arm_pace_required_balls, right_arm_wrist_spin_required_balls, right_arm_off_spin_required_balls, left_arm_pace_required_balls,
                                   left_arm_orthodox_required_balls, left_arm_wrist_required_balls])
    
    required_balls = required_balls[required_balls['player_dismissed'] == player]
    
    num_dismissals = len(required_balls)
        
    return num_dismissals

################################### END BATSMAN CORE ###################################

################################### BOWLER CORE ###################################

def wickets_taken(player, against_batsman, batting_types, innings_number, tournaments=None, venue=None, years=None, overs_range=None):
    """
        Total dismissals of this player given the conditions
        Args:
            player - (int) id of target player
            tournaments - (list of ints) list of tournament ids
            venue - (int) id of venue. 
            years - (list) list of years you want to consider
            overs_range - (list) 2 member list denoting [start_over, end_over]
            against_lhb - (boolean) mark it true if you want data only specific to left hand batters. dont mark this if you supply 'against_batsman'
            against_rhb - (boolean) mark it true if you want data only specific to right hand batters. dont mark this if you supply 'against_batsman'
            against_batsman - (int) id of specific bowler to find data against
            innings_number - (int) - 1 -> batting first 2 -> batting second 0 -> both
    """
    
    # Grabbing all balls bowled by this player
    required_balls = df_ball[df_ball["bowler"] == player]
    
    # Grabbing all matches to map ids
    required_matches = df_match
    
    # Run the required_matches dataframe through each match filter
    
    if tournaments is not None:
        required_matches = required_matches[required_matches['tournament_id'].isin(tournaments)]
        
    if venue is not None:
        required_matches = required_matches[required_matches['venue_id'] == venue]
        
    if years is not None:
        required_matches = required_matches[required_matches['match_date'].str.contains('|'.join(years))]
        
    match_ids_to_consider = np.array(required_matches['match_id'])
    required_balls = required_balls[required_balls['match_id'].isin(match_ids_to_consider)]
    
    if overs_range is not None:
        required_balls = required_balls[(required_balls['ball_number'] >= overs_range[0]) & (required_balls['ball_number'] <= overs_range[1])]
        
    if innings_number != 0:
        required_balls = required_balls[required_balls['innings_number'] == innings_number]
        
    if against_batsman != 'ALL':
        required_balls = required_balls[required_balls['batsman'] == against_batsman]
        
    # This section will be executed only if user has clicked any of the checkbox for batting types
    if any(bool_value for key, bool_value in batting_types.items()):
        
        # Creating empty dataframes for the balls bowled by different bowling types
        lhb_required_balls = pd.DataFrame(columns=required_balls.columns)
        rhb_required_balls = pd.DataFrame(columns=required_balls.columns)
        
        if batting_types["lh_bat_bool"]:
            lhb_required_balls = required_balls[required_balls['batsman'].isin(lhb_ID)]
        
        if batting_types["rh_bat_bool"]:
            rhb_required_balls = required_balls[required_balls['batsman'].isin(rhb_ID)]
            
        # pd.concat defaults to an "outer" merge (UNION)
        required_balls = pd.concat([lhb_required_balls, rhb_required_balls])
    
    total_balls_bowled = len(required_balls)
    
    all_dismissal_types = ['caught', 'obstructing the field', 'caught and bowled', 'bowled', 'run out', 'hit wicket', 'lbw', 'retired hurt', 'stumped']
    bowler_wicket_types = ['caught', 'caught and bowled', 'bowled', 'hit wicket', 'lbw', 'stumped']
    
    required_balls = required_balls[required_balls['dismissal_type'].isin(bowler_wicket_types)]
    
    total_wickets_taken = len(required_balls)
    
    return total_wickets_taken
    
    
    
def balls_bowled(player, against_batsman, batting_types, innings_number, tournaments=None, venue=None, years=None, overs_range=None):
    """
        Total dismissals of this player given the conditions
        Args:
            player - (int) id of target player
            tournaments - (list of ints) list of tournament ids
            venue - (int) id of venue. 
            years - (list) list of years you want to consider
            overs_range - (list) 2 member list denoting [start_over, end_over]
            against_lhb - (boolean) mark it true if you want data only specific to left hand batters. dont mark this if you supply 'against_batsman'
            against_rhb - (boolean) mark it true if you want data only specific to right hand batters. dont mark this if you supply 'against_batsman'
            against_batsman - (int) id of specific bowler to find data against
            innings_number - (int) - 1 -> batting first 2 -> batting second 0 -> both
    """
    
    # Grabbing all balls bowled by this player
    required_balls = df_ball[df_ball["bowler"] == player]
    
    # Grabbing all matches to map ids
    required_matches = df_match
    
    # Run the required_matches dataframe through each match filter
    
    if tournaments is not None:
        required_matches = required_matches[required_matches['tournament_id'].isin(tournaments)]
        
    if venue is not None:
        required_matches = required_matches[required_matches['venue_id'] == venue]
        
    if years is not None:
        required_matches = required_matches[required_matches['match_date'].str.contains('|'.join(years))]
        
    match_ids_to_consider = np.array(required_matches['match_id'])
    required_balls = required_balls[required_balls['match_id'].isin(match_ids_to_consider)]
    
    if overs_range is not None:
        required_balls = required_balls[(required_balls['ball_number'] >= overs_range[0]) & (required_balls['ball_number'] <= overs_range[1])]
        
    if innings_number != 0:
        required_balls = required_balls[required_balls['innings_number'] == innings_number]
        
    if against_batsman != 'ALL':
        required_balls = required_balls[required_balls['batsman'] == against_batsman]
        
    # This section will be executed only if user has clicked any of the checkbox for batting types
    if any(bool_value for key, bool_value in batting_types.items()):
        
        # Creating empty dataframes for the balls bowled by different bowling types
        lhb_required_balls = pd.DataFrame(columns=required_balls.columns)
        rhb_required_balls = pd.DataFrame(columns=required_balls.columns)
        
        if batting_types["lh_bat_bool"]:
            lhb_required_balls = required_balls[required_balls['batsman'].isin(lhb_ID)]
        
        if batting_types["rh_bat_bool"]:
            rhb_required_balls = required_balls[required_balls['batsman'].isin(rhb_ID)]
            
        # pd.concat defaults to an "outer" merge (UNION)
        required_balls = pd.concat([lhb_required_balls, rhb_required_balls])
    
    total_balls_bowled = len(required_balls)
    
    return total_balls_bowled


def runs_given(player, against_batsman, batting_types, innings_number, tournaments=None, venue=None, years=None, overs_range=None):
    """
        Total dismissals of this player given the conditions
        Args:
            player - (int) id of target player
            tournaments - (list of ints) list of tournament ids
            venue - (int) id of venue. 
            years - (list) list of years you want to consider
            overs_range - (list) 2 member list denoting [start_over, end_over]
            against_lhb - (boolean) mark it true if you want data only specific to left hand batters. dont mark this if you supply 'against_batsman'
            against_rhb - (boolean) mark it true if you want data only specific to right hand batters. dont mark this if you supply 'against_batsman'
            against_batsman - (int) id of specific bowler to find data against
            innings_number - (int) - 1 -> batting first 2 -> batting second 0 -> both
    """
    
    # Grabbing all balls bowled by this player
    required_balls = df_ball[df_ball["bowler"] == player]
    
    # Grabbing all matches to map ids
    required_matches = df_match
    
    # Run the required_matches dataframe through each match filter
    
    if tournaments is not None:
        required_matches = required_matches[required_matches['tournament_id'].isin(tournaments)]
        
    if venue is not None:
        required_matches = required_matches[required_matches['venue_id'] == venue]
        
    if years is not None:
        required_matches = required_matches[required_matches['match_date'].str.contains('|'.join(years))]
        
    match_ids_to_consider = np.array(required_matches['match_id'])
    required_balls = required_balls[required_balls['match_id'].isin(match_ids_to_consider)]
    
    if overs_range is not None:
        required_balls = required_balls[(required_balls['ball_number'] >= overs_range[0]) & (required_balls['ball_number'] <= overs_range[1])]
        
    if innings_number != 0:
        required_balls = required_balls[required_balls['innings_number'] == innings_number]
        
    if against_batsman != 'ALL':
        required_balls = required_balls[required_balls['batsman'] == against_batsman]
        
    # This section will be executed only if user has clicked any of the checkbox for batting types
    if any(bool_value for key, bool_value in batting_types.items()):
        
        # Creating empty dataframes for the balls bowled by different bowling types
        lhb_required_balls = pd.DataFrame(columns=required_balls.columns)
        rhb_required_balls = pd.DataFrame(columns=required_balls.columns)
        
        if batting_types["lh_bat_bool"]:
            lhb_required_balls = required_balls[required_balls['batsman'].isin(lhb_ID)]
        
        if batting_types["rh_bat_bool"]:
            rhb_required_balls = required_balls[required_balls['batsman'].isin(rhb_ID)]
            
        # pd.concat defaults to an "outer" merge (UNION)
        required_balls = pd.concat([lhb_required_balls, rhb_required_balls])
    
    total_runs_given = required_balls['total_runs'].sum()
    
    return total_runs_given


################################### END BOWLER CORE ###################################

################################### FANTASY CORE ###################################

def player_runs_by_match(player, recency_parameter):
    """
        Get a list of runs scored by this player in the past 'recency_parameter' matches
        Args:
            player - (int) id of target player
            recency_parameter - (int) denoting how many matches in the past you want data from
    """
    # Grab top 'recency_parameter' matches played by this player sorted in reverse chronological order
    required_matches = sorted(fantasy_obj[player].keys(), key=lambda match_id: match_id_date_map[match_id], reverse=True)[0:recency_parameter]
    
    match_runs = []
    for match in required_matches:
        total_runs_scored = 0
        # iterate over each bowling type to calculate total runs
        for bowling_type in fantasy_obj[player][match]['runs_scored']:
            total_runs_scored += fantasy_obj[player][match]['runs_scored'][bowling_type]
        match_runs.append(total_runs_scored)
    
    # reversing the array before sending for appropriate plotting
    return match_runs[::-1]

def player_wickets_by_match(player, recency_parameter):
    """
        Get a list of wickets taken by this player in the past 'recency_parameter' matches
        Args:
            player - (int) id of target player
            recency_parameter - (int) denoting how many matches in the past you want data from
    """
    # Grab top 'recency_parameter' matches played by this player sorted in reverse chronological order
    required_matches = sorted(fantasy_obj[player].keys(), key=lambda match_id: match_id_date_map[match_id], reverse=True)[0:recency_parameter]
    
    match_wickets = []
    for match in required_matches:
        total_wickets_taken = 0
        # iterate over each bowling type to calculate total runs
        for batting_type in fantasy_obj[player][match]['wickets_taken']:
            total_wickets_taken += fantasy_obj[player][match]['wickets_taken'][batting_type]
        match_wickets.append(total_wickets_taken)
        
    # reversing the array before sending for appropriate plotting
    return match_wickets[::-1]

def player_points_by_match(player, recency_parameter):
    """
        Get a list of points obtained by this player in the past 'recency_parameter' matches
        Args:
            player - (int) id of target player
            recency_parameter - (int) denoting how many matches in the past you want data from
    """
    # Grab top 'recency_parameter' matches played by this player sorted in reverse chronological order
    required_matches = sorted(fantasy_obj[player].keys(), key=lambda match_id: match_id_date_map[match_id], reverse=True)[0:recency_parameter]
    
    match_points = []
    for match in required_matches:
        total_points_obtained = fantasy_obj[player][match]['fantasy_points']
        match_points.append(total_points_obtained)
    
    # reversing the array before sending for appropriate plotting
    return match_points[::-1]

def player_runs_scored_against_bowling(player, recency_parameter):
    """
        Get a list of runs scored by this player in the past 'recency_parameter' matches against different bowling types
        Args:
            player - (int) id of target player
            recency_parameter - (int) denoting how many matches in the past you want data from
    """
    
    # Grab top 'recency_parameter' matches played by this player sorted in reverse chronological order
    required_matches = sorted(fantasy_obj[player].keys(), key=lambda match_id: match_id_date_map[match_id], reverse=True)[0:recency_parameter]
    
    # 6 values corresponsing to each different bowling type
    match_runs = [0, 0, 0, 0, 0, 0]
    for match in required_matches:
        # iterate over each bowling type to calculate total runs
        for bowling_type in fantasy_obj[player][match]['runs_scored']:
            if bowling_type == "Right arm Off spin":
                match_runs[0] += fantasy_obj[player][match]['runs_scored'][bowling_type]
            if bowling_type == "Left arm Orthodox":
                match_runs[1] += fantasy_obj[player][match]['runs_scored'][bowling_type]
            if bowling_type == "Right arm wrist spin":
                match_runs[2] += fantasy_obj[player][match]['runs_scored'][bowling_type]
            if bowling_type == "Right arm Pace":
                match_runs[3] += fantasy_obj[player][match]['runs_scored'][bowling_type]
            if bowling_type == "Left arm Pace":
                match_runs[4] += fantasy_obj[player][match]['runs_scored'][bowling_type]
            if bowling_type == "Left arm wrist":
                match_runs[5] += fantasy_obj[player][match]['runs_scored'][bowling_type]
                
    return match_runs

def player_wickets_taken_against_batting(player, recency_parameter):
    """
        Get a list of runs scored by this player in the past 'recency_parameter' matches against different bowling types
        Args:
            player - (int) id of target player
            recency_parameter - (int) denoting how many matches in the past you want data from
    """
    
    # Grab top 'recency_parameter' matches played by this player sorted in reverse chronological order
    required_matches = sorted(fantasy_obj[player].keys(), key=lambda match_id: match_id_date_map[match_id], reverse=True)[0:recency_parameter]
    
    # 6 values corresponsing to each different bowling type
    match_wickets = [0, 0]
    for match in required_matches:
        # iterate over each batting_type  to calculate total runs
        for batting_type in fantasy_obj[player][match]['wickets_taken']:
            if batting_type == "Left-hand bat":
                match_wickets[0] += fantasy_obj[player][match]['wickets_taken'][batting_type]
            if batting_type == "Right-hand bat":
                match_wickets[1] += fantasy_obj[player][match]['wickets_taken'][batting_type]
                
    return match_wickets

################################### END FANTASY CORE ###################################