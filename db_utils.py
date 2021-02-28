# Basic
from collections import Counter
import math
import numpy as np
import os
import pprint

# yaml specific
import yaml

# Data handling
import pandas as pd
from tqdm import tqdm

# Config variables
raw_data_path = "raw_data"
clean_data_path = "clean_data"
tournament_name = "IPL"

def update_player(update_column, update_value, check_column, check_value):
    """
    This function 
        - reads the player.csv file
        - updates update_column with update_value where check_column is check_value
        - writes it back
    Args:
        query_name - query name to be checked with
        players_with_same_surname - a subset of the players dataframe for checking with the query_name
    """
    
    #print(f"Updating {update_column} with {update_value} where {check_column} is {check_value}")
    players = pd.read_csv(os.path.join(clean_data_path, "player.csv"))
    players = players.loc[:, ~players.columns.str.contains('^Unnamed')]
    players.loc[players[check_column] == check_value, update_column] = update_value
    players.to_csv(os.path.join(clean_data_path, "player.csv"), index=False)
    
def add_player(player_display_name, player_name, player_full_name, batting_style, bowling_style, birthdate, country_id, list_team_ids):
    """
    This function 
        - reads the player.csv file
        - adds a new row to the players dataframe
        - writes it back
    Args:
        player_display_name -  name displayed in scorecards
        player_name - name
        player_full_name - full name
        batting_style - style
        bowling_style - style
        birthdate - date
        country_id - id of country the player belongs to
        list_team_ids - string of comma separated team_ids
    """
    
    player_csv = pd.read_csv(os.path.join(clean_data_path, "player.csv"))
    player_csv = player_csv.loc[:, ~player_csv.columns.str.contains('^Unnamed')]

    # if entry already exists, put peace
    if len(player_csv[player_csv["player_full_name"] == player_full_name]) > 0:
        return
    
    player_csv = player_csv.append({"player_id" : len(player_csv)+1, 
                                      "player_display_name" : player_display_name,
                                      "player_name" : player_name,
                                      "player_full_name" : player_full_name,
                                      "batting_style" : batting_style,
                                      "bowling_style" : bowling_style,
                                      "birthdate" : birthdate,
                                      "country_id" : country_id,
                                      "list_team_ids" : list_team_ids
                                     }, ignore_index=True)
    player_csv.to_csv(os.path.join(clean_data_path, "player.csv"), index=False)