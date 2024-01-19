Welcome to flavor space project! It is an expansion on my group project from Georgia Tech (https://github.com/jhwaffles/cse6242-team58-project). It leverages NLP and machine learning to generate flavor embeddings off of a recipe -> ingredient -> molecules data set. These embeddings are the basis of the recipe recommendation app based off of flavor profiles. There are some other fun features in this app - feel free to play around.

### Data sources:

- Recipe 1M+ dataset
- FlavorDB

### Methods:

- One hot encoded molecule vectors to make recipe molecule "documents"
- Trained gensim Doc2Vec model with recipe molecule document to make embeddings.
- These flavor embeddings are clustered with DBscan.
- Dimensional reductuion using Umap. This can be visualized in a 3D cluster browser.
- With these embeddings, recipes are searchable using similarity (distance).
- Recommedation of top recipes similar in flavor.
