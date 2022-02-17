# Resource Scraper 
Currently single threaded and basic. Goal is given a URL explore site tree and keep track of all PDF and IMG urls (jpg, png, tiff, gif). Will be useful for finding the menus on a website. 

Will be very useful when used in combination with OCR to determine if we have indeed found a menu.

## Sample usage
```
curl http://localhost:8080/get_resources?url=https://firehousepb.com/ 
```
### output
{
  "pdf_urls": [
    "https://firehousepb.com/wp-content/uploads/FH-Menu-12-15-21.pdf", 
    "https://firehousepb.com/wp-content/uploads/FH-drinkmenu-12.15.2021-.pdf"], 
  "img_urls": [
    "https://firehousepb.com/wp-content/uploads/IMG_5521.jpg", 
    "https://firehousepb.com/wp-content/uploads/IMG_5086.jpg",
    ...
  ]
}

##requirements
```
sudo apt-get update
sudo apt-get -y install python3-pip
pip3 install beautifulsoup4 flask flask_cors waitress 
```
