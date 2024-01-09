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
    df=proj_df.copy()
    newrow = pd.DataFrame([["None","ingredient"]], columns=['food','type'])
    df=pd.concat([df, newrow],ignore_index=True)
    st.text(len(df))
    #recipe_list = proj_df[proj_df['type'] == "recipe"]["food"].tolist()
    ingr_list = df[df['type'] == "ingredient"]["food"].tolist()
    ingr_list = ["None"]+ingr_list
    st.text("ingredients: {}".format(ingr_list))  
    model_list={"Flavor Model":flav_model}
    modelchoice = st.selectbox("Choose Model", list(model_list.keys()))

    
    word2vec=model_list[modelchoice] 
    A=word2vec.dv.vectors.copy()
    zero_row = np.zeros([1,A.shape[1]])
    A = np.vstack([A, zero_row])  #use this as vectors with 0 row for "None"
    st.text(A.shape)
    #word2vec = load_model(models[model_key])

    choice1 = st.selectbox("Add Ingredient 1", ingr_list)
    choice2 = st.selectbox("Add Ingredient 2", ingr_list)
    choice3 = st.selectbox("Add Ingredient 3", ingr_list)

    topn = 10
    if choice1 and choice2 and choice3:
        idx1=food2index(df[df["type"]=='ingredient'],choice1)
        idx2=food2index(df[df["type"]=='ingredient'],choice2)
        idx3=food2index(df[df["type"]=='ingredient'],choice3)

        st.text(idx1)
        st.text(idx2)
        st.text(idx3)

        similars = word2vec.dv.most_similar(positive=[A[idx1]+A[idx2]+A[idx3]])
    
    s_df = pd.DataFrame(similars, columns=['id','similarity']).astype({'id': 'string'})
    s_df.reset_index().merge(df, on='id', how='left')[['id','similarity','food']]


    #st.dataframe(pd.DataFrame(s_df, columns=["id", "similarity"]))
            
    # st.subheader("If A-->B, then C-->?? Example: Man --> King, then Woman --> Queen")
    # wordA = st.text_input("A")
    # wordB = st.text_input("B")
    # wordC = st.text_input("C")
    # if wordA and wordB and wordC:
    #     output = word2vec.most_similar_cosmul(positive=[wordB.lower(), wordC.lower()], negative=[wordA.lower()])
    #     st.dataframe(pd.DataFrame(output, columns=["Word", "Score"]))
        
    
if __name__ == "__main__":
    main()