import requests
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup, SoupStrainer


app = Flask('paddington')
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        url = data.get('url')
        print(f"Received URL: {url}")
        response_ai = generate_request(url)
        return jsonify({"result": response_ai}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def load_env():
    try:
        with open(os.path.join(os.path.dirname(__file__), '.env'), 'r') as f:
            for line in f:
                if line.startswith('PPX_API_KEY='):
                    return line.strip().split('=')[1]
    except Exception as err:
        print(f"[!] Failed to read the Perplexity API key from the .env file: {err}")
    return None

API_KEY = load_env()

if not API_KEY:
    print("[!] API key not recognized.")
    exit(1)

def generate_request(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/',
    'Accept-Language': 'en-US,en;q=0.9',
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
    "TE": "trailers"
    }

    # make the request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        article = SoupStrainer([
        "p",        # Paragraphs
        "span",     # Inline text
        "div",      # Divs, often containers
        "section",  # Sections of the document
        "article",  # Main article content
        "li",       # List items
        "a",        # Anchor links, sometimes contain inline text
        "h1", "h2", "h3", "h4", "h5", "h6",  # Headers
        "blockquote",  # Quotes or citations
        "em", "strong",  # Emphasized or bold text
        "td", "th",  # Table cells
        "summary",  # Collapsible summary details
        "details",  # Details/hidden content
        "nav",  # Navigation menu
        "aside",  # Sidebar content
        "footer",  # Footer text
        ])
        soup = BeautifulSoup(response.text, "html.parser", parse_only=article)

        if soup and soup.text.strip():
            contents = str(soup)
        else:
            return "[!] Article content not found"
    else:
        return f"[!] Website blocked the request. Status code {response.status_code}"
    url_ppx = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""Using the following contents of a article/news website, first extract the article, then read the article, examine the article, examine the platform, the tone, and the word choices to determine if there is any bias in the political leaning in the article.
             Format: 'Author: <if you think the author has a personal bias or not (about 50-75 characters)> 
             Platform: <bias information on the author (about 75-150 characters)> 
             Tone: <bias information on the tone of the article, conclude this after reading through the article and analysing the tone (about 75-150 characters)> 
             Additional: <additional bias information you need to conclude after reading the article (about 25-35 words long)> '

    IMPORTANT: Don't say left or right wing/leaning, instead use other terms like liberal and conservative
    "(about xxxx words long)" IS INSTRUCTIONS FOR YOU! DO NOT INCLUDE IT IN THE FINAL RESPONSE!!!
    "(about xxxx characters long)" IS INSTRUCTIONS FOR YOU! DO NOT INCLUDE IT IN THE FINAL RESPONSE!!!
    
    Don't say things other than the bias analysis like “certainly!” or a concluding statement

    If the contents of the webpage are broken or if you are unable to view it correctly or there isn't enough text from the article to determine a bias, output “[!] Webpage error.”

    DO NOT output anything other than the political leaning analysed.

    Contents of the webpage = {contents}")
    """

    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are an AI used to determine if certain articles/news are politically biased."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }

    try:
        response = requests.post(url_ppx, json=data, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as err:
        return f"[!] Error: {err}"

if __name__ == '__main__':
    app.run(port=5000, debug=False)
