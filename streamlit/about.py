# streamlit components
import streamlit as st

from PIL import Image

def main(match_format, session_state):
    st.title("Welcome to Cricboard")
    
    st.write("""
    You can choose to see a quick demo through this [video](https://youtu.be/dMnsE7TbO4Q) if you're lazy to read below. 
    - First we have a sidebar that contains a match format option (T20, TEST, ODI). Choose this first. This option would be applicable across all pages. (Currently we have loaded only IPL data, but in the future we want to show stats for all tournaments and formats as well)
    - Next we have 3 pages "Fantasy - Player Comparisons", "Batting Stats", "Bowling Stats" that you can navigate across through the sidebar. These are the 3 pages we have as of now. We definitely would try to add more pages with more plots. If you guys have some ideas for some new features please do let us know :)  """)
    with st.beta_expander("Fantasy - Player Comparisons"):
        st.write("""
        - The Fantasy page is purely targetted towards comparing different players. The basic idea is that users have around 30 mins to choose their fantasy teams between the time of toss (and playing squad release) and time of match start. So we want to provide some information that could potentially be useful to you in picking your best team. 
            - First choose the match date.
            - Then choose a match from the dropdown of matches thats happening on this particular date. You will now be able to see a table of the current squad of both teams. 
            - Then the "Choose players to compare" section will be populated with the current squad of both teams. You can choose how many ever players to compare, but the plots tend to get cramped up if you choose more than 4 or 5 players. 
            - Now you will be able to see a series of plots divided across 3 sections. 
                - The "ALL TIME STATS COMPARISON" is to give a quick overview of the players' all-time abilities. The 3 plots you see denote "Average runs per match", "Average wickets per match" and "Average points per match". (We detail more about how points are calculated in a later section). You can now choose 3 filters that would affect the plots. 
                    - Stats specific to this current venue. 
                    - Stats specific to the player's opposition. (eg. If you are comparing Rohit Sharma and Virat Kohli where the selected match is MI vs RCB, Rohit's stats are specific to matches against RCB and Kohli's stats are specific to matches against MI)
                    - Stats specific to innings number (If you want to compare how players fare while batting first or chasing)
                - The "RECENT FORM COMPARISON" is to give an idea of how these players have performed in the last n matches. You can configure the value of n with what we call as the "recency parameter". You should be able to see 3 line charts denoting runs, wickets and fantasy points. Each chart would contain k different lines, with k denoting the number of players you have chosen to compare.  
                - The "PLAYER SKILL ANALYSIS" is to show the distribution of the players stats across different bowling/batting styles. You can check the batting and bowling styles of all players in this match in the table shown in the top.
            - These are currently what we have in the fantasy section. If you think there are some more insights that you want to see before choosing your team, please contact us, we would definitely try to implement them right away.""")

    with st.beta_expander("Batting Stats"):
        st.write("""
        - The Batting page is targetted towards getting batting related stats given the variety of conditions.
            - The stats we currently show are:
                - Runs
                - Strike Rate
                - Average
                - Dismissals
            - You have 2 options as to how you want to list stats:
                - Top n performers. Input a number in the "Choose top n" to see who are the best n players given the conditions. 
                - Single player stats. Input a player from the dropdown in the "Choose a single player". Make sure "Choose top n" is set to 0 to see single player stats.
            - Now we have a wide range of input filters that you can configure to see some really really cool insights for different players.     
                - The period you want to consider - this is a slider input to see how the player has played in a certain years range. 
                - The venue you want to consider - choose a venue to see how the players have played in this specific venue. 
                - Innings number - takes one out of 3 values. 0 (both innings), 1 (batting first), 2 (batting second)
                - Overs range - this is again a slider input to see how the players fare across different sections of the match (eg. Powerplay, middle overs, death, etc..,)
                - Min runs scored - this is to set a minimum threshold of players to consider for strike rate and average. Default - 100 runs
            - Bowling type checkboxes:
                - Choose 'Against pace' for only pace specific stats.
                - Choose 'Against spin' for only spin specific stats.
                - If you want more detailed bowling types choose the other checkboxes like "left arm wrist". Make sure 'Against spin' and 'Against pace' are unchecked when you are choosing the more specific bowling types.
            - Against a specific bowler = choose a bowler from the dropdown to see stas specific to the faceoff between this particular batsman and this particular bowler.""")
    with st.beta_expander("Bowling Stats"):
        st.write("""
        - The Bowling page is targetted towards getting bowling related stats given the variety of conditions.
            - The stats we currently show are:
                - Wickets
                - Strike Rate
                - Average
                - Economy
            - The input section is very similar to the batting page and is self explanatory.""")
        