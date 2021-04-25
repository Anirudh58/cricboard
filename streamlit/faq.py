# streamlit components
import streamlit as st

from PIL import Image

def main(match_format, session_state):
    st.title("FAQ")
    
    with st.beta_expander("Who can use this tool?"):
        st.markdown("""
        - If you are looking to just get some cool cricket insights. 
        - If you are looking for more information that could possibly help you choose your fantasy team.
        """)
        
    with st.beta_expander("How are we different from other stats websites?"):
        st.markdown("""
        - We don't really want to convince you as to why this tool is *different* or *better*, its upto you guys to decide. But two basic driving factors that we felt were missing in other sites were:
            - Lack of interactivity
            - Inability to input compound filters while getting stats. 
        """)
        
    with st.beta_expander("Why did we build this?"):
        st.markdown("""
        - We love cricket 
        - We thought this was cool 
        - We learnt a lot in the process 
        """)
        
    with st.beta_expander("What is the source behind all our stats?"):
        st.write("""
        - All ours stats are coded from scratch through ball-by-ball data obtained from [cricsheet](https://cricsheet.org/). We cannot thank this page enough for providing and maintaining this data. 
        - All player details were scraped from [cricinfo](https://www.espncricinfo.com/)
        """)
        
    with st.beta_expander("How did we validate our insights?"):
        st.write("""
        - Every time we code a new stat, we try to validate it through all time stats found in official websites. eg: After we built the top runs scorers stat, we checked it (with no filters) with the official IPL site for top runs scorers to make sure what we have is correct. Now we can choose to play around with different parameters.
        """)
        
    with st.beta_expander("How accurate are these stats?"):
        st.write("""
        - The accuracy of all these stats are fully dependent on the data we use through [cricsheet](https://cricsheet.org/). As far as we know, they guys at cricsheet do a pretty good job of validating all data. However, it is likely that there might be some small mistakes that have creeped in. But the basic idea is to see the big picture and hence we feel these minor discrepancies can be overlooked. 
        """)
    
    with st.beta_expander("How are the fantasy points calculated?"):
        st.write("""
        - The fantasy points have again been calculated from scratch based on the current [official dream 11 scoring rules](https://www.dream11.com/games/point-system). The scoring system may differ across different fantasy websites but we chose Dream 11 due to its popularity. 
        """)
        
    with st.beta_expander("Some things we are working on"):
        st.write("""
        We sort of hurried to put things up right before IPL starts. Apart from the various insights/plots, some features that we are working on are:
        - Maintaing state between pages. Currently pages get reset when you navigate between them, we will try to avoid them. 
        - Loading data from other tournaments. eg: It would certainly make more sense to see how Maxwell has played in BBL or T20I recently rather than just relying on last years IPL data.
        - Calculating "top n" stats in the batting/bowling page is pretty slow because we literally loop through every ball played by every player. We are trying to see if some optimaztion/precomputing is possible, but until then please do bear the latency. 
        - Option to directly share an insight/plot to twitter. 
        """)
        
    with st.beta_expander("Long term ambitious goals"):
        st.write("""
        - BCCI official website now contains ball tacking information as well. If this data is soon available in a standardized format we would love to incorporate this information to provide more interesting insights. 
        - Highly interested in doing video analytics. Scene segmentation, shot classification, Automated commentary generation, etc. Although they may not have real useful applications, I would love to experiment with these problem statements. 
        """)
    
    st.markdown("""
    ***
    """)
    
    with st.beta_expander("Disclaimer"):
        st.write("""
        - This is a free tool purely built out of interest. We are completely not responsible for any money lost through fantasy games based on data from this site. 
        """)
    
    with st.beta_expander("Support"):
        st.write("""
        - We built this in the past few weeks with our full-time jobs occupying most of our time. There is certainly so much scope for improvement so please do contact us if you have any sort of feedback (bugs, factual mistakes, feature suggestions, new plot ideas, etc..,) and we would try to work on them if time permits. We had a lot of fun working on this project with zero experience in sports analytics and we certainly hope to work on more cool stuff in the future. Thanks for visiting and please do quote us if you share something from here on social media :) 
        """)
        
    with st.beta_expander("About us"):
        
        col1, col2, col3, col4, col5 = st.beta_columns((1, 2, 2, 2, 1))
        
        with col2:
            image = Image.open('./assets/images/anip.jpg')
            image = image.resize((250, 200))
            st.image(image, caption='Anirudh Prabakaran')
        
        with col3:
            image = Image.open('./assets/images/rishab.jpeg')
            image = image.resize((250, 200))
            st.image(image, caption='Rishabraj Dhariwal')
            
        with col4:
            image = Image.open('./assets/images/vivek.jfif')
            image = image.resize((250, 200))
            st.image(image, caption='Vivek Subramaniam')
        
        col1, col2, col3 = st.beta_columns((1, 12, 1))
        
        with col2:
            st.markdown("""
            We are yet another bunch of college friends who spend a significant portion of our daily lives thinking about/watching/playing cricket. We started working on this project purely out of interest just to get some cool insights, but later we decided to put our work into some UI and share it to people. Feel free to contact us for anything through linkedin ([Anirudh](https://www.linkedin.com/in/anirudh-prabakaran/), [Rishab](https://www.linkedin.com/in/rishab9797/), [Vivek](https://www.linkedin.com/in/vivek-sambamurthy/)) or twitter ([Anirudh](https://twitter.com/Anip58), [Rishab](https://twitter.com/RishabD9797), [Vivek](https://twitter.com/viveks1996))
            """)