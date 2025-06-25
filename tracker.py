from flask import Flask, request, jsonify
import sqlite3
import pandas
from sklearn.metrics.pairwise import cosine_similarity
import numpy

app = Flask(__name__)

# Database Setup
def init_db():
    with sqlite3.connect('user-data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interactions (
            user_id TEXT,
            product_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, product_id)
            )
            ''')
            conn.commit()

init_db()

# Track user interactions
@app.route('/track', methods=['POST'])
def track_interaction():
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')

    with sqlite3.connect('user_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO user_interactions (user_id, product_id)
            VALUES (?, ?)
            ''', (user_id, product_id))
            conn.commit()

        return jsonify ({"message": "Interaction tracked"})

# Recommend products based on user habits
@app.route('/recommend/<user_id>', methods=['GET'])
def recommend(user_id):
    with sqlite3.connect('user_data.db') as conn:
        query = '''
        SELECT product_id, COUNT(*) as interaction_count
        FROM   user_interactions
        WHERE user_id = ?
        GROUP BY product_id
    '''
    df = pandas.read_sql_query(query, conn, params=(user_id,))

if df.empty:
    return jsonify({"message": "No interactions found for this user."})

    # Example: Recommend products based on interaction counts (simple recommendation)
    recommended_products = df.sort_values(by='interaction_count', ascending=False).head(5)
    return jsonify(recommended_products.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

    
