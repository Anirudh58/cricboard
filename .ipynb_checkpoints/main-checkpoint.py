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

# viz
import streamlit as st

# my library
from db_utils import update_player, add_player 
from infra import create_session_state
import batsman, bowler


# Global constants
PAGES = {
    "Batsman": batsman,
    "Bowler": bowler
}

# use @st.cache whenever you want caching mechanisms for fast loading
# These formats will not change
@st.cache
def populate_formats():
    formats = ["TEST", "ODI", "T20"]
    return formats

def main():
    # session variables
    session = create_session_state()
    
    
    st.sidebar.title("CRICBOARD")
        
    # First user needs to choose a format that will be applicable across all pages
    match_format = st.sidebar.selectbox("Choose a format", populate_formats())
        
    # Navigation where users can move across different pages
    st.sidebar.title('Navigation')
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page = PAGES[selection]
    page.main(match_format)
        
    
if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="CRICBOARD", page_icon="./assets/images/logo.png")
    main()