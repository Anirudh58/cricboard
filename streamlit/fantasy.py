# bread and butter
from matplotlib import pyplot as plt 
import numpy as np
import os
import pandas as pd
from pathlib import Path
import sys

# streamlit components
import streamlit as st

# my lib
from src.insights import batting_total_runs, batting_strike_rate, batting_average

# Config variables
raw_data_path = "raw_data"
clean_data_path = "clean_data"

@st.cache
def choose_matches(match_date):
    match_list = ["CSK vs MI", "RCB vs DC"]
    return match_list

@st.cache
def populate_players(select_match):
    player_list = ["MSD", "VK"]
    
    return player_list

def main(match_format):
    st.title("Fantasy - UI Rough Design")
    st.markdown("Helping you pick your best Dream 11 team")
                
    col1, col2 = st.beta_columns((1, 1))
    
    with col1:
        match_date = st.date_input("Match Date")
        #st.write(f"match_date: {match_date}")
    
    with col2:
        select_match = st.selectbox("Choose match", options=choose_matches(match_date))
                
                
    col1, col2, col3 = st.beta_columns((1, 2, 1))
    
    with col2:
        players_list = st.multiselect("Choose upto 5 players to compare:", options=populate_players(select_match))  
        
        
    col1, col2, col3 = st.beta_columns((1, 2, 1))
    
    with col2:
        recency_parameter = st.slider("Recency parameter ", min_value=1, max_value=20, value=1, step=1, format="%d")
                
    col1, col2, col3 = st.beta_columns((1, 1, 1))
    
    # Runs scored
    with col1:
        st.header("Runs Comparison")
        runs_comparison = pd.DataFrame(np.random.randn(recency_parameter, 5), columns=['player 1', 'player 2', 'player 3', 'player 4', 'player 5'])
        st.line_chart(runs_comparison)
        
    # Wickets taken
    with col2:
        st.header("Wickets Comparison")
        wickets_comparison = pd.DataFrame(np.random.randn(recency_parameter, 5), columns=['player 1', 'player 2', 'player 3', 'player 4', 'player 5'])
        st.line_chart(wickets_comparison)
        
    # Fantasy points
    with col3:
        st.header("Fantasy Comparison")
        fantasy_points = pd.DataFrame(np.random.randn(recency_parameter, 5), columns=['player 1', 'player 2', 'player 3', 'player 4', 'player 5'])
        st.line_chart(fantasy_points)
        
        
    col1, col2, col3, col4 = st.beta_columns((1, 1, 1, 1))
    
    # First pie chart -> Percentage distribution of runs scored with respect to bowling types
    with col1:
        st.header("Runs Scored vs Bowling")
        
        # Creating dataset 
        bowling_types = ['LEFT SPIN', 'RIGHT ARM PACE', 'LEFT ARM PACE'] 
        values = [23, 17, 35] 

        # Creating plot 
        fig = plt.figure(figsize =(6, 4)) 
        plt.pie(values, labels = bowling_types) 
        
        st.pyplot(fig)
        
    # Table giving them information about who are the bowlers of the above types
    with col2:
        st.header("Bowlers in opposition")
        bowlers = pd.DataFrame([["JADDU", "BOOM", "NATTU"]], columns=['LEFT SPIN', 'RIGHT ARM PACE', 'LEFT ARM PACE'])
        st.table(bowlers)
        
    # First pie chart -> Percentage distribution of runs scored with respect to bowling types
    with col3:
        st.header("Runs Scored vs Bowling")
        
        # Creating dataset 
        bowling_types = ['LEFT SPIN', 'RIGHT ARM PACE', 'LEFT ARM PACE'] 
        values = [23, 17, 35] 

        # Creating plot 
        fig = plt.figure(figsize =(6, 4))
        plt.pie(values, labels = bowling_types) 
        
        st.pyplot(fig)
        
    # Table giving them information about who are the bowlers of the above types
    with col4:
        st.header("Bowlers in opposition")
        bowlers = pd.DataFrame([["JADDU", "BOOM", "NATTU"]], columns=['LEFT SPIN', 'RIGHT ARM PACE', 'LEFT ARM PACE'])
        st.table(bowlers)
        
        
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
