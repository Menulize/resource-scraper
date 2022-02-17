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

@app.route("/get_resources", methods = ['GET'])
def get_resources():
    url = request.args.get("url") 
    max_crawl_depth = request.args.get("max_crawl_depth", default=3)

    visited = set()
    pdfs = []
    images = []
    def crawl(url, depth):
        if url in visited:
            return
        if depth > max_crawl_depth:
            return

        visited.add(url)
        
        try:
            page = requests.get(url)
        except:
            return

        soup = BeautifulSoup(page.content, "html.parser")
        links = [a.get('href') for a in soup.findAll("a")]
        hostname = url.split("//")[1].split("/")[0] 
        links = list(set(filter(
            lambda url: 
                (url is not None and 
                    'http' in url and 
                    hostname in url) and 
                        ("." not in url.split("/")[-1] or 
                        ".html" in url or 
                        ".htm" in url or 
                        ".php" in url), links)))
        
        new_pdfs = [a.get('href') for a in soup.findAll("a")]
        new_pdfs = list(set(filter(lambda url: url is not None and ".pdf" in url, new_pdfs)))
        pdfs.extend(new_pdfs)
        
        new_images = [a.get('src') for a in soup.findAll("img")]
        images.extend(new_images)
        
        new_images_links = list(set(filter(lambda url: url.lower().split(".")[-1] in ['jpg', 'jpeg', 'png', 'gif', 'tiff'],  [a.get('href') for a in soup.findAll("a")])))
        images.extend(new_images_links)

        for link in links:
            crawl(link, depth + 1)
    crawl(url, 0)
    
    return json.dumps({ "pdf_urls": list(set(pdfs)), "img_urls": list(set(images)) })

    ## Crawl site for all images (need to work on filter) 

    ## For each PDF and image.. OCR them if they say contain menu and combine them 

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
