import streamlit as st


def main(match_format):
    st.title("Bowler")
    #st.markdown("This page will contain some general stats specific to bowling")
    
    '''
    Each insight is going to consist of the following sections
    1) header - Name of the stat
    2) subheader - Brief description of the stat
    3) input section - a section where the parameters to the stat can be interactively controlled
    4) output section - a section where the output is displayed in some cool UI (if possible)
    '''
    
    
    st.header("Total Wickets")
    st.markdown(f"Total wickets taken across all tournaments in {match_format}s")