# simple_crawler
Very simple Webcrawler written in python for learning purposes.

It get some seed pages, scan for all URL's and store then in a SQLITE3 database, counting how many references for each URL.

## Running
Just do:
$ python webcrawler.py

## Chaging the URL seeds

Edit the webcrawler.py file changing the URL and html file storage:

seeds = [{'page': 'http://www.someurlsite.com', 'file': 'html/someurlsite.html'},...]
