import os
import requests
from time import sleep
from scrapeutils import *

# Settings

DIR_LINKS = "links" # Links directory
SUBDIRS_LINKS = [] # Links subdirectories to check
DIR_OUTPUTS = "outputs" # Outputs directory

DEFAULT_TLD = ".ca" # TLD to be used if none is specified in an entry
WAIT_TIME_NEXT_PAGE = 2 # Time in seconds to wait between each different page load
WAIT_TIME_REATTEMPT = 4 # Time in seconds to wait after a page load error
MAX_ATTEMPTS = 3 # Maximum number of attempts at fetching a particular page

# Collect user-provided Amazon URLs from DIR_LINKS and given subdirectories.

links_raw = []

for root, dirs, files in os.walk(DIR_LINKS):
	if root == DIR_LINKS or root in os.path.join(DIR_LINKS, SUBDIRS_LINKS):
		for file_ in files:
			with open(os.path.join(DIR_LINKS, file_), 'r') as f:
				links_raw += f.read().split('\n')

# Reformat the URLs
urls = (generateURL(line, default_tld=DEFAULT_TLD) for line in links_raw)

# Main loop

headers = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Language": "en-US,en;q=0.5",
			"Accept-Encoding": "gzip, deflate",
			"Cache-Control": "max-age=0",
			"Connection": "keep-alive",
			"DNT": '1',
			"TE": "trailers",
			"Upgrade-Insecure-Requests": '1' }
data = {}

for url in urls:

	product_data = []
	first_page = True
	page_number, num_pages = 1, 1

	while page_number <= num_pages:

		for i in range(MAX_ATTEMPTS):
			headers["User Agent"] = generateUserAgent()
			print(page_number)
			page = requests.get(url, headers=headers).text
			if "Sorry! Something went wrong." not in page:
				break
			sleep(WAIT_TIME_REATTEMPT)
		else:
			raise Exception("Could not access: " + url)

		if first_page:
			first_page = False
			link_info = extractLinkInfo(page)
			product_name = link_info["product_name"]
			num_pages = link_info["num_pages"]

		product_data += extractContent(page)
		url = nextPage(url)
		page_number += 1
		sleep(WAIT_TIME_NEXT_PAGE)

	data[product_name] = product_data

print(data)

'''
file_list = os.listdir(DIR_LINKS)
print(file_list)


with open(os.path.join(DIR_LINKS, file_list[0]), 'r') as f:
	print(os.path.join(DIR_LINKS, file_list[0]))
	print(f.read())
'''
