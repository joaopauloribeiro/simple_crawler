import requests
import re
import json

def get_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def get_page(url, filename):
    print("getting page:", url, " saving in file:", filename)
    if not re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url, flags=re.IGNORECASE):
        print("Invalid url", url)
        return -1
    
    try:
        config = get_config()
        timeout = config.get('crawler', {}).get('timeout', 10)
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # The requests library automatically decodes content.
        # We can specify the encoding if we know it, or let requests handle it.
        # The original code used "latin-1", so we will stick with it for now.
        response.encoding = 'latin-1'
        
        with open(filename, "w", encoding='latin-1') as f:
            f.write(response.text)
            
        return 0
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return -1

if __name__ == '__main__':
    filename = "html/test_90832910381.html"
    url = "http://yahoo.com"
    get_page(url, filename)
    # file_test = open(filename, "rt")
    # print(file_test.read())
    url = "yahoo.com"
    get_page(url, filename)
