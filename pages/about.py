import streamlit as st
import numpy as np

projection_df=st.session_state["projection_df"]
cluster_groups=st.session_state["cluster_groups"]
df=st.session_state['df_small.pkl']

#cluster browser portion
st.header("INFO only")
st.dataframe(df)