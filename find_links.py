from bs4 import BeautifulSoup
from urllib.parse import urljoin

def find_links(filename, base_url):
    """
    Finds all the links in an HTML file.
    
    Args:
        filename (str): The path to the HTML file.
        base_url (str): The base URL of the page, used to resolve relative links.
        
    Returns:
        list: A list of tuples, where each tuple contains the absolute URL and the link text.
    """
    with open(filename, 'r', encoding='latin-1') as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Ignore anchors
        if href.startswith('#'):
            continue
            
        absolute_url = urljoin(base_url, href)
        link_text = a_tag.get_text(strip=True)
        links.append((absolute_url, link_text))
        
    return links

if __name__ == '__main__':
    # Example usage:
    # Create a dummy html file for testing
    dummy_html_file = 'test_links.html'
    with open(dummy_html_file, 'w') as f:
        f.write('''
            <html>
                <body>
                    <a href="http://example.com/page1">Page 1</a>
                    <a href="/page2">Page 2</a>
                    <a href="page3">Page 3</a>
                    <a href="#section">Section</a>
                    <a href="http://another.com/page4">Page 4</a>
                </body>
            </html>
        ''')
    
    base_url = 'http://example.com/some/path/'
    page_links = find_links(dummy_html_file, base_url)
    print(f"Base URL: {base_url}")
    print("Links found:")
    for url, text in page_links:
        print(f"  - {url} ('{text}')")
    
    # Expected output:
    # http://example.com/page1
    # http://example.com/page2
    # http://example.com/some/path/page3
    # http://another.com/page4

    import os
    os.remove(dummy_html_file)
