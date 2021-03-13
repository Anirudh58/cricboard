import base64
import sys

from streamlit.report_thread import get_report_ctx
import streamlit as st

class session_state(object):
    """
    An object to maintain session state variables as attributes
    """
    
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

'''
Suppose we want to open a database connection that can be reused across multiple runs of a Streamlit app. For this you can make use of the fact that cached objects are stored by reference to automatically initialize and reuse the connection:
Use the allow_output_mutation=True flag to suppress the immutability check. This prevents Streamlit from trying to hash the output connection, and also turns off Streamlit’s mutation warning in the process.
'''                   
@st.cache(allow_output_mutation=True)
def get_session(id, **kwargs):
    return session_state(**kwargs)

def create_session_state(**kwargs):
    ctx = get_report_ctx()
    id = ctx.session_id
    return get_session(id, **kwargs)
