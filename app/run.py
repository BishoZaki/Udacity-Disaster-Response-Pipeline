#imports 
import json
import plotly
import pandas as pd
import numpy as np

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from flask import Flask
from flask import render_template, request
from plotly.graph_objs import Bar
import joblib
from sqlalchemy import create_engine

#initialize
app = Flask(__name__)

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)
    
    return clean_tokens

#load data
engine = create_engine('sqlite:///../data/DisasterResponse.db')
df = pd.read_sql_table('FigureEight', engine)

#load model
model = joblib.load("../models/classifier.pkl") #NEED TO CHANGE

#index webpage displays cool visuals and recieves user input text for model
@app.route('/')
@app.route('/index')

def index():

    #extract data needed for visuals 
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)

    #show distribution of different categories
    category = list(df.columns[4:])
    category_counts = []
    for column_name in category:
        category_counts.append(np.sum(df[column_name]))
    
    #extract data exclude related
    categories = df.iloc[:, 4:]
    categories_mean = categories.mean().sort_values(ascending=False)[1:11]
    categories_names = list(categories_mean.index)

    #create visuals
    graphs = [
        {
            'data': [
                Bar(
                    x=genre_names,
                    y=genre_counts
                )
            ],
            'layout': {
                'title': 'Distribution of Message Genres',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Genre"
                }
            }
        },
        {
            'data':[
                Bar(
                    x=category,
                    y=category_counts
                )
            ],
            'layout': {
                'title': 'Distribution of Message Categories',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Category"
                }
            }
        },
        {
            'data': [
                Bar(
                    x=categories_names,
                    y=categories_mean
                )
            ],
            'layout': {
                'title': 'Top 10 Message Categories',
                'yaxis': {
                    'title': "Percenatge"
                },
                'xaxis': {
                    'title': "Categories"
                }
            }
        }
    ]

    #encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    #render web page with plotly graphs
    return render_template('master.html', ids = ids, graphJSON= graphJSON)

# webpage that handles user query and displays model results
@app.route('/go')
def go():
    #save user input in query
    query = request.args.get('query', '')

    #use model to predict classification query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    #this will render go.html 
    return render_template(
        'go.html',
        query=query,
        classification_result = classification_results
    )

def main():
    app.run(host='0.0.0.0', port=3001, debug=True)

if __name__ == '__main__':
    main()
