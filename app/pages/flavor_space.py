import plotly.express as px
import streamlit as st

projection_df=st.session_state["projection_df"]
cluster_groups=st.session_state["cluster_groups"]

st.header("Flavor Space - 3D Cluster Browser")

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
