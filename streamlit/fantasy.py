# bread and butter
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

