
import plotly.express as px
import streamlit as st
import numpy as np
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

projection_df=st.session_state["projection_df"]
cluster_groups=st.session_state["cluster_groups"]

#cluster browser portion
st.header("Have user select a cluster. Look at Tables below")

#st.table(cluster_groups)
unique_clusters=sorted(projection_df["cluster"].unique())
option = st.selectbox(
    'Select a Cluster',unique_clusters)

limit_row_choices=[10,20,50,len(projection_df)]
limit = st.selectbox('Limit Rows',limit_row_choices)
table_view=projection_df[projection_df["cluster"]==option][["cluster","food",'ingredient_count']].iloc[:limit,:]

#view table.
st.table(table_view)


#word cloud
dfd=cluster_groups[cluster_groups["cluster"]==option]
ab=list(dfd["flav_freq"].values)[0]

wordcloud = WordCloud().generate_from_frequencies(ab)
fig, ax = plt.subplots()
ax.imshow(wordcloud)
ax.axis("off")
st.pyplot(fig)

#word cloud tf-idf


def tf_idf_(df,dict_column):
    #convertsincorporate and update into original dataframe.
    #df_output=expand_dataframe(df,dict_column)

#calculate tf (this is the weight)

#calculate number of documents
    n_doc=len(df)
#calculate how many times it pops up in documents
    tf_matrix=df['flav_freq'].apply(pd.Series)
    tf_sums=tf_matrix.fillna(0).astype(bool).sum(axis=0)
    n_doc=df.shape[0]
#formula. tf-idf=tf/log(n_doc/tf_sums)
    IDF=np.log(n_doc/tf_sums)
    output=tf_matrix*IDF  #converted to TF_IDFs. high freq=0
    dict=output.fillna(0).T.to_dict()

    ccc=df.copy()
    ccc["flav_freq_idf"]=dict
    return ccc
ccc=tf_idf_(cluster_groups,"flav_freq")

dfd=ccc[ccc["cluster"]==option]
ab=list(dfd["flav_freq_idf"].values)[0]
wordcloud_tf_idf = WordCloud().generate_from_frequencies(ab)
fig2, ax2 = plt.subplots()
ax2.imshow(wordcloud_tf_idf)
ax2.axis("off")
st.pyplot(fig2)
