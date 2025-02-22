from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

app = Flask(__name__)

def seo_audit(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract SEO elements
        title_tag = soup.find('title')
        title = title_tag.text if title_tag else 'Missing'
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else 'Missing'
        
        h1_tags = [h1.text.strip() for h1 in soup.find_all('h1')]
        
        # Find broken links
        broken_links = []
        for link in soup.find_all('a', href=True):
            link_url = urljoin(url, link['href'])
            if not re.match(r'^https?:', link_url):
                continue
            try:
                link_response = requests.head(link_url, allow_redirects=True, timeout=5)
                if link_response.status_code >= 400:
                    broken_links.append(link_url)
            except requests.RequestException:
                broken_links.append(link_url)
        
        load_time = response.elapsed.total_seconds()
        
        # Mobile-Friendliness Check (Basic viewport meta tag detection)
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        mobile_friendly = bool(viewport_meta)
        
        # Core Web Vitals Placeholder (LCP, FID, CLS)
        core_web_vitals = {
            'LCP': 'Data not available via basic requests',
            'FID': 'Data not available via basic requests',
            'CLS': 'Data not available via basic requests'
        }
        
        return {
            'title': title,
            'metaDescription': description,
            'h1Tags': h1_tags,
            'brokenLinks': broken_links,
            'loadTime': load_time,
            'mobileFriendly': mobile_friendly,
            'coreWebVitals': core_web_vitals
        }
    except requests.RequestException as e:
        return {'error': str(e)}

@app.route('/api/seo-audit', methods=['POST'])
def audit_endpoint():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    results = seo_audit(url)
    return jsonify(results)


import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Default to port 10000 if not set
    app.run(host="0.0.0.0", port=port)
