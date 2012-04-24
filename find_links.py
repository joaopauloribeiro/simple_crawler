'''
Created on Apr 22, 2012

@author: lordzeus
'''
import sys
import re
import urllib
import html_unescape

def find_links(filename):
	page = open(filename, "rt").read()
	links = re.findall(r'<a.*?href=[\'"]([^#].*?)[\'"].*?>(.*?)</a>',page, flags=re.IGNORECASE)
	links_clean = []
	for link in links:
		name = re.sub("<.*?>","",link[1],flags=re.IGNORECASE)
		name = html_unescape.unescape(name)
		links_clean.append((link[0],name))
	return links_clean

if __name__ == '__main__':
	page = "html/about.html"
	page_links = find_links(page)
	print(page_links)
