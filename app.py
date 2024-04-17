
import numpy as np
import pandas as pd
import streamlit as st
import gensim
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.markdown("""
        <style>
               .block-container {
                    padding-top: 2rem;
                    padding-bottom: 0rem;
                    padding-left: 2rem;
                    padding-right: 2rem;
                }
        </style>
        """, unsafe_allow_html=True)
st.header("Welcome to the Flavor Space app!")
st.caption("How to use: This application aims to make recipe recommendations to the user that will satisfy their cravings with an optional nutritional ranking. First, select an input recipe as a starting point. This could be anything like 'Orange BBQ Pork Ribs'. Next, select a desired dietary preference. The top 10 recipe alternatives with ***similar flavor profiles*** are listed, scored by nutritional content.")

st.caption("For example, if 'ketogenic' is selected, recipes with a higher daily value % of protein and fat will be prioritized and listed first. Daily value (DV%) for each macronutrient is calculated from nutrition value per 100g of food divided by daily nutrition recommended value, per FDA recommendation.")

st.caption("For more information on cluster browsing, follow the link to visualize flavor space on the side panel. For more details on the data and modeling, please follow the link to 'about'.")

##imports
projection_df=pd.read_pickle("data/projection_df.pkl")
if 'projection_df' not in st.session_state:
    st.session_state['projection_df']=projection_df


cluster_groups=pd.read_pickle("data/cluster_groups.pkl")
if 'cluster_groups' not in st.session_state:
    st.session_state['cluster_groups']=cluster_groups

df=pd.read_pickle("data/df_small.pkl")
if 'df_small.pkl' not in st.session_state:
    st.session_state['df_small.pkl']=df

MODEL_FILES = {'cbow-400': 'data/flavor2vec-cbow.model'}
model = gensim.models.doc2vec.Doc2Vec.load(MODEL_FILES['cbow-400'])
if 'model' not in st.session_state:
    st.session_state['model']=model

##app
#scoring system
def Score(dict_TopRecipe_ntr, preference):
    dv = [2000,78,50,6,20,50]
    
    if preference == 'Default':
        parameter = [-1,0,1,-1,0,-1]
    elif preference == 'Ketogenic':
        parameter = [0,1,1,-1,-0.5,-1]
    elif preference == 'Low Fat':
        parameter = [0,-1,1,-1,-1,-1]

    dict_score = {}
    dict_energy = {}
    for i, row in dict_TopRecipe_ntr.iterrows():
        
        nutrient = [
            row['nutr_values_per100g.energy'], 
            row['nutr_values_per100g.fat'],
            row['nutr_values_per100g.protein'],
            row['nutr_values_per100g.salt'],
            row['nutr_values_per100g.saturates'],
            row['nutr_values_per100g.sugars']
        ]
        
        pct_dv = [a/b for a,b in zip(nutrient,dv)]
        wt_score = [a*b for a,b in zip(parameter,pct_dv)]
        score = sum(wt_score)
        dict_score[row['id']] = score
    
    dict_score_rank = pd.DataFrame(dict_score.items(), columns=['id', 'ntr_score'])
    return dict_score_rank.sort_values(by=['ntr_score'], ascending=False)

#helper function
# def NtrDataFlat(TopRecipe):
#     ntr_temp = TopRecipe['nutr_values_per100g']
#     df_ntr = pd.DataFrame.from_dict({(i): ntr_temp[i] for i in ntr_temp.keys()}, orient='index')
#     return TopRecipe.merge(df_ntr, left_index=True, right_index=True)
def food2id(df,food):  #convert food to id#
    return df['id'].to_numpy()[df['food'].to_numpy() == food].item()
    
def id2food(df,id):
    return df['food'].to_numpy()[df['id'].to_numpy() == id].item()

def food2index(df,lookup):
    return df[df["food"]==lookup][:1].index.item()

def id2index(df,lookup):
    return df[df["id"]==lookup][:1].index.item()

def dataframe_with_selections(df):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)



def NutritionOptimize(s_df, df, preference = 'Default'):    
    TopRecipe = df.loc[df['id'].isin(s_df['id'])]
    #TopRecipe=df['code2'].to_numpy()[df['code1'].to_numpy() == code].item()
    #print(TopRecipe)
    #rank the recipe
    top_n_recipe_score = Score(TopRecipe, preference)
    
    #prepare pandas table output
    out = top_n_recipe_score.merge(TopRecipe, left_on='id', right_on='id')                            
    out['%DV-energy'] = out['nutr_values_per100g.energy']*100/2000
    out['%DV-fat'] = out['nutr_values_per100g.fat']*100/78
    out['%DV-protein'] = out['nutr_values_per100g.protein']*100/50
    out['%DV-salt'] = out['nutr_values_per100g.salt']*100/6
    out['%DV-saturates'] = out['nutr_values_per100g.saturates']*100/20
    out['%DV-sugars'] = out['nutr_values_per100g.sugars']*100/50
    out = out[['id','food','%DV-energy','%DV-fat','%DV-protein','%DV-salt','%DV-saturates','%DV-sugars']]
    return out.round(1)
def PlotNutritionDV(NtrOptimize_df):
    color = NtrColor(NtrOptimize_df)
    ntr_plot = pd.DataFrame({'Nutrition':['energy', 'fat', 'protein', 'salt', 'saturates', 'sugars'], 
                             '% Daily Value':[NtrOptimize_df['%DV-energy'].iloc[0], 
                                              NtrOptimize_df['%DV-fat'].iloc[0], 
                                              NtrOptimize_df['%DV-protein'].iloc[0],
                                              NtrOptimize_df['%DV-salt'].iloc[0],
                                              NtrOptimize_df['%DV-saturates'].iloc[0],
                                              NtrOptimize_df['%DV-sugars'].iloc[0]]})
    ntr_plot.plot.bar(x='Nutrition', y='% Daily Value', title=NtrOptimize_df['food'].item(), rot=0,
                       color=color,figsize=(3,3),fontsize=8)
    #heper function
def NtrColor(NtrOptimize_df):
    color = []
    col = '#E0E0E0'
    for column in NtrOptimize_df:
        if column in ['%DV-salt', '%DV-saturates', '%DV-sugars']:
            if NtrOptimize_df[column].iloc[0] < 5.0:
                col = '#5DA573'
            elif (NtrOptimize_df[column].iloc[0] >= 5.0) and (NtrOptimize_df[column].iloc[0] < 20.0):
                col = '#FFCC99'
            else:
                col = '#CC6600'
            
        elif column in ['%DV-fat', '%DV-protein']:
            if NtrOptimize_df[column].iloc[0] < 5.0:
                col = '#CC6600'
            elif (NtrOptimize_df[column].iloc[0] >= 5.0) and (NtrOptimize_df[column].iloc[0] < 20.0):
                col = '#B1D1BA'
            elif NtrOptimize_df[column].iloc[0] >= 20.0:
                col = '#5DA573'

        color.append(col)
    return color[2:]




recipe_list = projection_df[projection_df['type'] == "recipe" ]["food"].tolist()

preference_list=["Default","Ketogenic","Low Fat"]
#ingr = st.slider('Minimum # Ingredients', 0,10,1)
# & (projection_df['ingredient_count'] >=)

col1, col2 = st.columns([1,1])

choice = col1.selectbox("Choose Starting Recipe", recipe_list)
diet_choice = col1.selectbox("Choose Dietary preference", preference_list, help='Selecting different diet will change the coefficients that determine rankings. For example, the **default** diet will reward :green[protein] while penalizing :red[carbs, sugars, salts]. Selecting **Ketogenic** diet will reward :green[fats and proteins] and penalize :red[sugars, salts, and saturates]. Selecting **low fat** will penalize :red[fats, saturates, salts, and sugars].')


idx1=food2index(df,choice)
A=model.dv.vectors.copy()
similars = model.dv.most_similar(positive=[A[idx1]])
s_df = pd.DataFrame(similars, columns=['id','similarity']).astype({'id': 'string'})
#s_df.reset_index().merge(df, on='id', how='left')[["id", "food","type", "similarity","ingredient_count"]]


nutritional_opt_df = NutritionOptimize(s_df, df,diet_choice)


selection = dataframe_with_selections(nutritional_opt_df)[:1]
st.write("Your selection:")
st.write(selection)

st.set_option('deprecation.showPyplotGlobalUse', False)

if selection.empty:
    st.text('No Recipes Selected!')
else:
    nutrition_bars = PlotNutritionDV(selection)
    st.pyplot(nutrition_bars)