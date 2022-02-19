import json
import requests

from bs4 import BeautifulSoup
import pdb

from flask import Flask, request 
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

@app.route("/check")
def check():
    return json.dumps({})

headers = { 
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1" 
}

@app.route("/get_resources", methods = ['GET'])
def get_resources():
    url = request.args.get("url") 
    max_crawl_depth = request.args.get("max_crawl_depth", default=2)

    visited = set()
    pdfs = []
    images = []
    pages = []
    
    def clean_url(url):
        return url.split("#")[0]

    def crawl(url, depth):
        if clean_url(url) in visited:
            return
        if depth > max_crawl_depth:
            return

        visited.add(clean_url(url))
        
        try:
            page = requests.get(url, headers=headers)
        except Exception as e:
            print(e)
            return

        soup = BeautifulSoup(page.content, "html.parser")
        links = [a.get('href') for a in soup.findAll("a")]
        hostname = url.split("//")[1].split("/")[0] 
        links = list(set(filter(
            lambda url: 
                (url is not None and 
                    ('http' in url or "/" == url[0] or "./" == url[:2]) and 
                    (hostname in url or "/" == url[0] or "./" == url[:2])) and 
                        ("." not in url.split("/")[-1] or 
                        ".html" in url or 
                        ".htm" in url or 
                        ".php" in url), links)))
        new_pdfs = [a.get('href') for a in soup.findAll("a")]
        new_pdfs = list(set(filter(lambda url: url is not None and ".pdf" in url, new_pdfs)))
        pdfs.extend(new_pdfs)
        
        new_images = list(set(filter(lambda url: url != None and ("http" in url or "/" == url[0] or "./" == url[:2]), [a.get('src') for a in soup.findAll("img")])))
        images.extend(new_images)
        
        new_images_links = list(set(filter(lambda url: url != None and url.lower().split(".")[-1] in ['jpg', 'jpeg', 'png', 'gif', 'tiff'],  [a.get('href') for a in soup.findAll("a")])))
        images.extend(new_images_links)

        # Scrape all the text on the page
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())

        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)
        pages.append({ "text": text, "url": url })

        for link in links:
            relative = False
            if link[0] == "/":
                link = hostname + link
                relative = True
            elif link[:2] == "./":
                link = hostname + "/" + link[2:]
                relative = True
            if relative:
                if 'https' in url:
                    link = 'https://' + link
                else:
                    link = 'http://' + link

            crawl(link, depth + 1)
    crawl(url, 0)
    
    return json.dumps({ "pdf_urls": list(set(pdfs)), "img_urls": list(set(images)), "pages": pages })

    ## Crawl site for all images (need to work on filter) 

    ## For each PDF and image.. OCR them if they say contain menu and combine them 

if __name__ == "__main__":
    app.run()
