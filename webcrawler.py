'''
Created on Apr 22, 2012

@author: lordzeus
'''
import time
import get_page
import find_links
import url_store

seeds = [{'page':'http://www.opovo.com.br', 'file':'html/opovo.html'},{'page':'http://www.globo.com', 'file':'html/globo.html'},{'page':'http://www.r7.com', 'file':'html/r7.html'},{'page':'http://www.uol.com.br', 'file':'html/uol.html'},{'page':'http://about.com', 'file':'html/about.html'}]
#seeds = [{'page':'http://google.com', 'file':'html/google.html'},{'page':'http://www.uol.com.br', 'file':'html/uol.html'},{'page':'http://www.opovo.com.br', 'file':'html/opovo.html'},{'page':'http://www.globo.com', 'file':'html/globo.html'}]
#seeds = [{'page':'http://google.com', 'file':'html/google.html'},{'page':'http://yahoo.com', 'file':'html/yahoo.html'},{'page':'http://about.com', 'file':'html/about.html'},{'page':'http://uol.com.br', 'file':'html/uol.html'},{'page':'http://globo.com', 'file':'html/globo.html'},{'page':'http://terra.com.br', 'file':'html/terra.html'}]

def main():
	def random_file(link):
		return "html/test_"+str(int(time.time()))+".html"

	c = url_store.init_db()
	seed_links = []
	#stored_links = url_store.get_urls(seed['page'], c)
	stored_links = {}
	#find primary links
	for seed in seeds:
		print("Adding links for ", seed['page']," saving in file: ", seed['file'])
		try:
			page_flag = get_page.get_page(seed['page'], seed['file'])
		except:
			continue
		if page_flag == -1:
			continue
		try:
			seed_links = find_links.find_links(seed['file'])
		except:
			continue
		for link in seed_links:
			if link[0] not in stored_links:
				#print("Adding link: ", link[0], "for page: ", seed['page'])
				stored_links[link[0]] = seed['page']
			else:
				print("Link already added", link[0])
	#add primary links to database
	#total_links = len(stored_links.keys())
	#link_index = 1
	#for link_stored in stored_links:
	#	print("Adding link #", link_index, "of ", total_links, "... ", stored_links[link_stored], link_stored)
	#	url_store.insert_url(stored_links[link_stored], link_stored, c)
	#	link_index += 1 

	#find secondary links
	secondary_links = stored_links.copy()
	for seed in stored_links:
		print("Searching links in ", seed)
		filename = random_file(seed)
		try:
			page_flag = get_page.get_page(seed, filename)
		except:
			continue
		if page_flag == -1:
			continue
		try:
			seed_links = find_links.find_links(filename)
		except:
			continue
		for link in seed_links:
			if link[0] not in secondary_links:
				print("Adding secondary link...", link[0])
				secondary_links[link[0]] = seed
			else:
				print("Link secondary already added", link[0])
	total_links = len(secondary_links.keys())
	link_index = 1
	for link_secondary in secondary_links:
		print("Adding link #", link_index, "of ", total_links, "... ", secondary_links[link_secondary], link_secondary)
		url_store.insert_url(secondary_links[link_secondary], link_secondary, c)
		link_index += 1 


	url_store.close_db(c)

if __name__ == '__main__':
	main()
