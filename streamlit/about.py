# streamlit components
import streamlit as st

from PIL import Image

def main(match_format, session_state):
    st.title("Welcome to Cricboard")
    
    with st.beta_expander("Who are we?"):
        
        col1, col2, col3, col4, col5 = st.beta_columns((1, 2, 2, 2, 1))
        
        with col2:
            image = Image.open('./assets/images/anip.jpg')
            image = image.resize((300, 200))
            #st.image(image, caption='Anirudh Prabakaran')
            #st.markdown("""
            #[linkedin](https://www.linkedin.com/in/anirudh-prabakaran/) [twitter](https://twitter.com/Anip58)
            #""")
            #st.write("[linkedin](https://www.linkedin.com/in/anirudh-prabakaran/)") #[linkedin](https://www.linkedin.com/in/anirudh-prabakaran/) [twitter](https://twitter.com/Anip58)
        
        with col3:
            image = Image.open('./assets/images/rishab.jfif')
            image = image.resize((300, 200))
            #st.image(image, caption='Rishabraj Dhariwal')
            
        with col4:
            image = Image.open('./assets/images/vivek.jfif')
            image = image.resize((300, 200))
            #st.image(image, caption='Vivek Subramaniam')
        
        col1, col2, col3 = st.beta_columns((1, 10, 1))
        
        with col2:
            st.markdown("""
            We are yet another bunch of college friends who spend a significant portion of our daily lives thinking about/watching/playing cricket. We started working on this project purely out of interest just to get some cool stats, but later we decided to put our work into some UI and share it to everyone. Contact us through linkedin ([Anirudh](https://www.linkedin.com/in/anirudh-prabakaran/), [Rishab](https://www.linkedin.com/in/rishab9797/), [Vivek](https://www.linkedin.com/in/vivek-sambamurthy/)) or twitter ([Anirudh](https://twitter.com/Anip58), [Rishab](https://twitter.com/RishabD9797), [Vivek](https://twitter.com/viveks1996))
            """)
    
    with st.beta_expander("Why did we build this?"):
        st.markdown("""
        - We love cricket 
        - We thought this was cool 
        - We learnt a lot in the process 
        """)
        
    with st.beta_expander("How are we different from other stats websites?"):
        st.markdown("""
        - We don't really want to convince you as to why this tool is *different* or *better*, its upto you guys to decide. But two basic driving factors that we felt were missing in other sites were:
            - Lack of interactivity
            - Inability to input multiple filters while getting stats. 
        """)
        
    with st.beta_expander("Who can use this tool?"):
        st.markdown("""
        - If you are looking to just get some cool cricket insights. 
        - If you are looking for more information that could possibly help you choose your fantasy team.
        """)
        
    with st.beta_expander("Overview of this tool"):
        st.write("""
        Now that we have established some basic things, lets dive in. You can choose to see a quick demo through this video if you're lazy to read below. 
        - First we have a sidebar that contains a match format option (T20, TEST, ODI). Choose this first. This option would be applicable across all pages. (Currently we have loaded only IPL data, but in the future we want to show stats for all tournaments and formats as well)
        - Next we have 3 pages "FANTASY", "BATTING", "BOWLING" that you can navigate across. 
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
                - The "PLAYER SKILL ANALYSIS" is to show the distribution of the players stats across different bowling/batting styles. You can check the batting and bowling styles of all players in this match in the table shown above.
            - These are currently what we have in the fantasy section. If you think there are some more insights that you want to see before choosing your team, please contact us, we would definitely try to implement them right away.
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
                - Against a specific bowler = choose a bowler from the dropdown to see stas specific to the faceoff between this particular batsman and this particular bowler.
        - The Bowling page is targetted towards getting bowling related stats given the variety of conditions.
            - The stats we currently show are:
                - Wickets
                - Strike Rate
                - Average
                - Economy
            - The input section is very similar to the batting page and is self explanatory. 
        - These are the 3 pages we have as of now. We definitely would try to add more pages with more plots. If you guys have some ideas for some new features please do let us know :) 
            
        """)
        
    with st.beta_expander("What is the source behind all our stats?"):
        st.write("""
        - All ours stats are coded from scratch through ball-by-ball data obtained from [cricsheet](https://cricsheet.org/) We cannot thank this page enough for providing and maintaining this data. 
        - All player details were scraped from [cricinfo](https://www.espncricinfo.com/)
        """)
        
    with st.beta_expander("How did we validate our insights?"):
        st.write("""
        - Every time we code a new stat, we try to validate it through all time stats found in official websites. eg: After we built the top runs scorers stat, we checked it (with no filters) with the official ipl site for top runs scorers to make sure what we have is correct. Now we can choose to play around with different parameters. 
        """)
        
    with st.beta_expander("How accurate are these stats?"):
        st.write("""
        - The accuracy of all these stats are 100% dependent on the data we use through [cricsheet](https://cricsheet.org/). It is highly likely that there might be some small ball level discrepancies or some matches may not have been recorded (this is not true for IPL as we know for sure that every single match has been accounted for). But the basic idea is to see the big picture and hence we feel these minor discrepancies can be overlooked. 
        """)
    
    with st.beta_expander("How are the fantasy points calculated?"):
        st.write("""
        - The fantasy points have again been calculated from scratch based on the current [official dream 11 scoring rules](https://www.dream11.com/games/point-system). The scoring system may differ across different fantasy websites but we chose Dream 11 due to its popularity. 
        """)
        
    with st.beta_expander("Disclaimer"):
        st.write("""
        - This is a free tool purely built out of interest. We are completely not responsible for any money lost through fantasy games based on data from this site. 
        """)
