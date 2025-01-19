import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get API keys from environment variables
YOUTUBE_API_KEY = os.getenv("YOUR_YOUTUBE_API_KEY")
REDDIT_CLIENT_ID = os.getenv("YOUR_REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("YOUR_REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("YOUR_REDDIT_USER_AGENT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# YouTube API setup (YouTube Data API v3)
YOUTUBE_SEARCH_API_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"

# Reddit API setup (using Reddit's API)
REDDIT_API_URL = 'https://www.reddit.com/r/{subreddit}/search.json'

# Placeholder for product research data
product_research_data = {}

# Function to get YouTube data
def get_youtube_data(product):
    search_params = {
        'part': 'snippet',
        'q': product,
        'key': YOUTUBE_API_KEY,
        'type': 'video',
        'maxResults': 5
    }
    search_response = requests.get(YOUTUBE_SEARCH_API_URL, params=search_params)
    search_results = search_response.json().get('items', [])

    youtube_data = []
    youtube_views = []
    video_ids = []

    for item in search_results:
        video_id = item['id']['videoId']
        video_ids.append(video_id)
        title = item['snippet']['title']
        url = f"https://www.youtube.com/watch?v={video_id}"
        youtube_data.append({'title': title, 'url': url})

    if video_ids:
        stats_params = {
            'part': 'statistics',
            'id': ','.join(video_ids),
            'key': YOUTUBE_API_KEY
        }
        stats_response = requests.get(YOUTUBE_VIDEOS_API_URL, params=stats_params)
        stats_results = stats_response.json().get('items', [])

        for i, stats in enumerate(stats_results):
            views = int(stats['statistics'].get('viewCount', 0))
            youtube_data[i]['views'] = views
            youtube_views.append(views)
    else:
        youtube_views = [0] * len(youtube_data)
        for data in youtube_data:
            data['views'] = 0

    return youtube_data, youtube_views

# Function to get Reddit data
def get_reddit_data(product):
    headers = {'User-Agent': REDDIT_USER_AGENT}
    params = {'q': product, 'limit': 5, 'sort': 'relevance', 'restrict_sr': False}
    response = requests.get(REDDIT_API_URL.format(subreddit='all'), headers=headers, params=params)
    reddit_data = []
    reddit_scores = []

    if response.status_code == 200:
        posts = response.json().get('data', {}).get('children', [])

        for post in posts:
            data = post['data']
            title = data['title']
            url = f"https://www.reddit.com{data['permalink']}"
            score = data['score']
            comments = data['num_comments']
            reddit_data.append({'title': title, 'url': url, 'score': score, 'comments': comments})
            reddit_scores.append(score)
    else:
        print(f"Error fetching Reddit data: {response.status_code}")
        reddit_data = []
        reddit_scores = []

    return reddit_data, reddit_scores

@app.route('/')
def serve_frontend():
    return render_template('index.html')  # Use render_template to render the page

# Endpoint to fetch research data based on product name
@app.route('/research/<product>', methods=['GET'])
def research(product):
    global product_research_data

    # Decode the product name
    from urllib.parse import unquote
    product = unquote(product)

    # Check if research data for the product exists in the cache
    if product in product_research_data:
        return jsonify(product_research_data[product])

    # Fetch YouTube data
    youtube_data, youtube_views = get_youtube_data(product)

    # Fetch Reddit data
    reddit_data, reddit_scores = get_reddit_data(product)

    # Cache the product research data
    product_research_data[product] = {
        'youtube_data': youtube_data,
        'youtube_views': youtube_views,
        'reddit_data': reddit_data,
        'reddit_scores': reddit_scores
    }

    # Return combined research data
    return jsonify(product_research_data[product])

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
