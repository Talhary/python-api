from flask import Flask, request, jsonify
from fuzzywuzzy import fuzz
import pandas as pd
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

# Load your dataset globally so it's only done once
df = pd.read_csv(r'\workspaces\python-api\finalData.csv')
df['Price'] = df['Price'].str.replace(',', '')
df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
df['Battery'] = df['Battery'].str.replace('mAh','')
df['Battery'] = pd.to_numeric(df['Battery'], errors='coerce').fillna(0)


@app.route('/search_phones', methods=['POST'])
def search_phones_api():
    # Parse the JSON sent in the request
    data = request.json
    name = data.get('name')
    storage = data.get('storage')
    battery = data.get('battery')
    max_price = data.get('max_price')
    min_price = data.get('min_price')
    rating_score = data.get('rating_score')

    # Call the search_phones function with the parameters
    results = search_phones(df, name, storage, battery, max_price, min_price, rating_score)
    # Convert the results to a list of dicts for JSON serialization
    results_list = results.to_dict('records')
    return jsonify(results_list)



def search_phones(df, name=None, storage=None, battery=None, max_price=None, min_price=None, rating_score=None):
    # Start with the full dataset
    results = df.copy()
    # Filter by each criterion
    if max_price:
        results = results[results['Price'] <= max_price]
    if min_price:
        results = results[results['Price'] >= min_price]
    if battery:
        results = results[results['Battery']>= battery]       
    if storage:
        storageString = str(storage)
        results = results[results['Storage'].str.contains(storageString, na=False)]
    if rating_score:
        
        results = results.sort_values(by='Rating Score', ascending=False)
        print('rating score called')
        # print(dff)
        
        # results = results.where(pd.notnull(results), None)

        # results = results.head(30)
             
        
    if name:
        # Use fuzzy matching to find close model names
        results['name_match_score'] = results['Name'].apply(lambda x: fuzz.partial_ratio(x.lower(), name.lower()))
        results = results[results['name_match_score'] > 70]  # Adjust the threshold as needed
    # Add more filters for other criteria if needed
    # ...
    if results.empty:
        return pd.DataFrame(columns=df.columns)
        
    
    
     # Check if 'name_match_score' column exists before sorting
    if 'name_match_score' in results.columns:
        recommended = results.sort_values(by='name_match_score', ascending=False)
    else:
        # If 'name_match_score' does not exist, return the results as is or sort by another relevant column
        recommended = results
    
    
    # Otherwise, sort by the match score and return the top results
    # recommended = search_results.sort_values(by='name_match_score', ascending=False)
    # replace the nan values with null for javascrip
    results = results.where(pd.notnull(results), None)

    return recommended.head(30)


if __name__ == '__main__':
    app.run(debug=True)
