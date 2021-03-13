# Basic
from collections import Counter
import datetime
import inspect
import math
import numpy as np
import os
import pprint
import sys

# yaml specific
import yaml

# Data handling
from fuzzywuzzy import fuzz, process
import pandas as pd
from tqdm import tqdm

# viz
import streamlit as st

# This is to add the root project folder to sys.path so that imports are easy
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

# my library
from infra import create_session_state
import batsman, bowler


# Global constants
PAGES = {
    "BATSMAN - GENERAL": batsman,
    "BOWLER - GENERAL": bowler
}

# use @st.cache whenever you want caching mechanisms for fast loading
# These formats will not change
@st.cache
def populate_formats():
    formats = ["T20", "ODI", "TEST"]
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