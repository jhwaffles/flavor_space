import os, sys
PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath("__file__")))
sys.path.append(PACKAGE_DIR)

import streamlit as st
from gensim.models import KeyedVectors
import gensim.downloader as api
import numpy as np
import pandas as pd


@st.cache(allow_output_mutation=True)
def load_model(model_name):
    word2vec = api.load(model_name)
    return word2vec

def food2id(df,food):  #convert food to id#
    return df['id'].to_numpy()[df['food'].to_numpy() == food].item()
    
def id2food(df,id):
    return df['food'].to_numpy()[df['id'].to_numpy() == id].item()

def food2index(df,lookup):
    return df[df["food"]==lookup].index.item()

def id2index(df,lookup):
    return df[df["id"]==lookup].index.item()

def main():
    flav_model=st.session_state["model"]
    proj_df=st.session_state["projection_df"]
    df=st.session_state['df_small.pkl']

    st.write(flav_model)
    st.header("\"Computational Cooking\"")
    st.caption("How to use:  Add ingredients to the 'recipe'. The table will display top searches in similarity from the sum of input ingredient vectors. The output can be filtered by 'ingredient only' or 'recipe only' as well as the minimum number of ingredients. By choosing 'ingredients only' it may be possible to come up with ingredient substitutes. Example: select garlic and 'ingredients only' the top outputs would be redskin onion, shitake, cherry tomatos, all ingredients with a 'umami' commponent. Another example:  select honey, peanut, cheese and the top result is 'Sweet Heat Sriracha Peacns'.")
    col3, col4 = st.columns([1,1])

    dfc=proj_df.copy()
    newrow = pd.DataFrame([["None","ingredient"]], columns=['food','type'])
    dfc=pd.concat([dfc, newrow],ignore_index=True)
    #st.text(len(df))
    #recipe_list = proj_df[proj_df['type'] == "recipe"]["food"].tolist()
    ingr_list = dfc[dfc['type'] == "ingredient"]["food"].tolist()
    ingr_list = ["None"]+ingr_list
    #st.text("ingredients: {}".format(ingr_list))  
   

    
    word2vec=flav_model
    A=word2vec.dv.vectors.copy()
    zero_row = np.zeros([1,A.shape[1]])
    A = np.vstack([A, zero_row])  #use this as vectors with 0 row for "None"
    choices=col3.multiselect("Add ingredients", ingr_list, key='build')

    #exclude=col3.multiselect("Substitute out", choices,key='substitute')
#find indexes 
    idx=[food2index(dfc[dfc["type"]=='ingredient'],i) for i in choices]
    #st.text(idx)
    try:
        similars = word2vec.dv.most_similar(positive=np.sum([A[i] for i in idx],axis=0),topn=1000)
        s_df = pd.DataFrame(similars, columns=['id','similarity']).astype({'id': 'string'})
        s_df.reset_index()
        option = st.selectbox('Search within:',('All','Ingredients Only', 'Recipes Only', ))
        #select minimum # ingredients
        if option!='Ingredients Only':
            ingr_min = st.slider('Minimum # ingredients', 0, 8, 2)
        #show top recipes.
        top_n = 10 #10 as default
        #st.write("Limit: ", top_n, ' rows')
        s_df=s_df.merge(df, on='id', how='left')[['id','similarity','food','type','ingredient_count']]
        if option=='Ingredients Only':
            s_df=s_df[s_df['type']=='ingredient']
        elif option=='Recipes Only':
            s_df=s_df[s_df['type']=='recipe']
            s_df=s_df[s_df['ingredient_count']>=ingr_min]
        else:
            s_df=s_df[s_df['ingredient_count']>=ingr_min]
        st.dataframe(s_df.iloc[:top_n,:],height = int(35.2*(5+1)))  #10 as default
    except TypeError:
        st.text("Input Ingredients")
    
    #select ingredient or recipe or both
    
    
if __name__ == "__main__":
    main()