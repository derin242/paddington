import requests
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

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
    url_ppx = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    source_code_response = requests.get(url)
    if source_code_response.status_code == 200:
        source_code = source_code_response.text
    else:
        print('[!] Couldn\'t get the source code for the website')

    prompt = f"""Using the following source code of a article/news website, read the article, examine the article, examine the author, the platform, the tone, and the word choices to determine if there is any bias in the political leaning in the article.
             Format: 'Author: <insert author name from the webpage, it will be like "By authorname" and you will find it from there> 
             Platform: <bias information on the author (about 75-150 characters)> 
             Tone: <bias information on the tone of the article, conclude this after reading through the article and analysing the tone (about 75-150 characters)> 
             Additional: <additional bias information you need to conclude after reading the article (about 25-35 words long)> '

    IMPORTANT: Don't say left or right wing/leaning, instead use other terms like liberal and conservative
    "(about xxxx words long)" IS INSTRUCTIONS FOR YOU! DO NOT INCLUDE IT IN THE FINAL RESPONSE!!!
    "(about xxxx characters long)" IS INSTRUCTIONS FOR YOU! DO NOT INCLUDE IT IN THE FINAL RESPONSE!!!
    
    Don't say things other than the bias analysis like “certainly!” or a concluding statement

    If the source code of the webpage is broken or if you are unable to view it correctly, output “[!] Invalid link.”

    DO NOT output anything other than the political leaning analysed.

    Source code of the webpage = {source_code}")
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
        with open('logs.txt', 'a') as f:
            f.write(f'{response.json()["choices"][0]["message"]["content"]}\n\n')
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as err:
        return f"[!] Error: {err}"

if __name__ == '__main__':
    app.run(port=5000, debug=False)
