import os
import json
from flask import Flask, render_template, jsonify, request
from news_service import fetch_all_news

app = Flask(__name__)

FAVORITES_FILE = "favorites.json"

def load_favorites():
    """Loads favorited articles from local JSON file."""
    if not os.path.exists(FAVORITES_FILE):
        return []
    try:
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading favorites file: {e}")
        return []

def save_favorites(favorites):
    """Saves favorited articles to local JSON file."""
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving favorites file: {e}")
        return False

@app.route('/')
def home():
    """Serves the front-end dashboard interface."""
    return render_template('index.html')

@app.route('/api/news', methods=['GET'])
def get_news():
    """Fetches combined and formatted news items."""
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    try:
        all_news = fetch_all_news(force_refresh=force_refresh)
        # Return all articles in a flat list
        return jsonify(all_news["all"])
    except Exception as e:
        print(f"Error in get_news api: {e}")
        return jsonify({"error": "Failed to load news data"}), 500

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """Returns the list of favorited articles."""
    return jsonify(load_favorites())

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """Adds a new article to the favorites list."""
    article = request.get_json()
    if not article or 'id' not in article:
        return jsonify({"error": "Invalid article data"}), 400
        
    favorites = load_favorites()
    # Check for duplicate
    if any(fav['id'] == article['id'] for fav in favorites):
        return jsonify({"message": "Article already favorited", "favorites": favorites}), 200
        
    favorites.append(article)
    if save_favorites(favorites):
        return jsonify({"message": "Article added to favorites", "favorites": favorites}), 201
    else:
        return jsonify({"error": "Failed to save to database"}), 500

@app.route('/api/favorites/<string:article_id>', methods=['DELETE'])
def remove_favorite(article_id):
    """Removes an article from the favorites list."""
    favorites = load_favorites()
    original_len = len(favorites)
    favorites = [fav for fav in favorites if fav['id'] != article_id]
    
    if len(favorites) == original_len:
        return jsonify({"error": "Article not found in favorites"}), 404
        
    if save_favorites(favorites):
        return jsonify({"message": "Article removed from favorites", "favorites": favorites}), 200
    else:
        return jsonify({"error": "Failed to update database"}), 500

@app.route('/api/sources', methods=['GET'])
def get_sources():
    """Computes and returns the set of active news sources."""
    try:
        all_news = fetch_all_news()
        sources = sorted(list(set(item['news_site'] for item in all_news["all"])))
        return jsonify(sources)
    except Exception as e:
        print(f"Error computing sources: {e}")
        return jsonify([]), 500

if __name__ == '__main__':
    # Start server locally on port 5000
    print("GingerNest News server starting at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
