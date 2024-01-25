import plotly.express as px
import streamlit as st

projection_df=st.session_state["projection_df"]
cluster_groups=st.session_state["cluster_groups"]

st.header("3D Cluster Browser")
st.caption("How to use:  After loading, examine how recipes are grouped in the 'flavor space', a representation of recipe-molecule embeddings in 3D space. Notice the groupings, e.g. 'citrus-y' clusters, or 'cheesy' clusters. Use in conjunction with 'Cluster Browser' to examine what flavors the model is able to pick up. ")
fig = px.scatter_3d(projection_df, 
                 x="x",
                 y="y",
                 z="z",
                 color="color",
                 symbol='cluster',
                 hover_data={"x":False,
                             "y":False,
                             "color":False,
                             "food":True,
                             "cluster":True
                             }
)
fig.update_traces(marker_size=3)
fig.update_layout(showlegend=False,
    autosize=True,width=600,
    height=600
)
st.plotly_chart(fig, use_container_width=True)
