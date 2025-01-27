import random
import re

def generateUserAgent(platform="random", browser="random"):
	""" Generates a random but coherent user agent. """
	# Generate OS
	
	if platform == "random":
		platform = random.choice(["win", "mac", "lin"])
	
	if platform.lower() == "win":
		os_ver = random.choice(["6.0", "6.1", "6.2", "6.3", "10.0"])
		arch = random.choice(["", "; WOW64", "; Win64; x64"])
		os = "Mozilla/5.0 (Windows NT {}{}".format(os_ver, arch)
		
	elif platform.lower() == "mac":
		os_ver = random.randint(6, 14)
		os = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.{}".format(os_ver)
		
	elif platform.lower() == "lin":
		os_ver = random.choice(["", "Ubuntu; ", "Fedora; "])
		arch = random.choice(["x86_64", "i686"])
		os = "Mozilla/5.0 (X11; {}Linux {}".format(os_ver, arch)
	
	else:
		raise Exception("Invalid platform type. Supported inputs: win, mac, lin")
	
	# Generate browser

	if browser == "random":
		browser = random.choice(["chrome", "firefox"])

	if browser.lower() == "chrome":
		# Last supported version on Vista and OS X 10.6, 10.7 and 10.8
		if os_ver in ["6.0", 6, 7, 8]:
			browser_ver = "49.0.2623.112"
		# Last supported version on OS X 10.9
		elif os_ver == 9:
			browser_ver = "65.0.3325.181"
		else:
			browser_ver = random.choice(["79.0.3945.79", "78.0.3904.70",
										"77.0.3865.120", "76.0.3809.132"])
		return "{}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36".format(os, browser_ver)

	elif browser == "firefox":
		# Last supported version on Vista
		if os_ver == "6.0":
			browser_ver = "51.0"
		# Last supported version on OS X 10.6, 10.7 and 10.8
		elif os_ver in [6, 7, 8]:
			browser_ver = "47.0"
		else:
			browser_ver = random.choice(["72.0", "71.0", "70.0", "69.0",
										 "68.0", "67.0", "66.0", "65.0",
										 "64.0", "63.0", "62.0", "61.0",
										 "60.0", "59.0", "58.0", "57.0"])
		return "{}; rv:{}) Gecko/20100101 Firefox/{}".format(os, browser_ver, browser_ver)

	else:
		raise Exception("Invalid browser type. Supported inputs: chrome, firefox")

def extractContent(page_content):

	""" Extracts product listings from the full page's HTML. Outputs a
		list comprised of one dict for each listing, which contains the
		following information:
		{ item_cost(str), ship_cost(str), condition(str), seller(str),
		avg_rating(str), num_ratings(int), pos_feedback(str), desc(str),
		origin(str), amazon_fulfill(bool) }. """
	
	extracted_data = []
	regex_split = "<div class=\"a-row a-spacing-mini olpOffer\" role=\"row\">"
	regex_cost = "(?<=[\$£₹])( ?\d{1,3}(\,\d{3})*\.\d{2})"
	regex_cond = "((Used|Collectible)\s+\-\s+(Acceptable|Good|Very Good|Like New)|New)\s*(?=</span>)"
	regex_seller = "seller=\w{12,14}.*?(?=</a>)|Warehouse Deals"
	regex_avg_rating = "\d\.?\d?(?= out of 5 stars)"
	regex_num_ratings = "(\d{1,3}(\,\d{3})*)(?= total ratings?\))"
	regex_pos_feedback = "\d{1,3}(?=% positive</b>)"
	regex_desc = "(?<=<div class=\"comments\">)[\s\S]*?(?=</div>)"
	regex_origin = "(?<=<span class=\"a-list-item\">)\s*Ships from[\s\S]*?(?=\.\n)"
	regex_fulfill = "Fulfill?ment by Amazon"
	
	split_page = re.split(regex_split, page_content)[1:]
	
	for listing in split_page:

		# Item and shipping costs, TODO: rewrite to handle prices in the product description
		price_search = re.findall(regex_cost, listing)
		assert len(price_search) > 0, "Could not find price"
		item_cost = price_search[0][0].strip()
		ship_cost = price_search[1][0].strip() if len(price_search) > 1 else "0.00"
		
		# Item condition
		condition_raw = re.findall(regex_cond, listing)
		assert len(condition_raw) > 0, "Could not find item condition"
		condition = ' '.join(condition_raw[0][0].split())
				
		# Seller
		seller_search = re.findall(regex_seller, listing)
		if len(seller_search) > 0:
			if "Warehouse Deals" in seller_search[0]:
				seller = "Amazon Warehouse Deals"
			else:
				seller_raw = seller_search[0]
				seller_index = int(re.search('>', seller_raw).span()[1]) # TODO: Rewrite to handle seller names including '>'
				seller = seller_raw[seller_index:]
		else:
			seller = "Amazon"
		
		# Average rating
		avg_rating_raw = re.findall(regex_avg_rating, listing)
		avg_rating = avg_rating_raw[0] if len(avg_rating_raw) > 0 else "N/A"
		
		# Total number of ratings
		num_ratings_raw = re.findall(regex_num_ratings, listing)
		num_ratings = int(num_ratings_raw[0][0].replace(',', '')) if len(num_ratings_raw) > 0 else 0

		# Percentage of positive feedback
		pos_feedback_raw = re.findall(regex_pos_feedback, listing)
		pos_feedback = pos_feedback_raw[0] if len(pos_feedback_raw) > 0 else "N/A"
		
		# Item description
		desc_raw = re.findall(regex_desc, listing)
		desc = desc_raw[0].strip() if len(desc_raw) > 0 else "N/A"
		
		# Seller origin
		origin_raw = re.findall(regex_origin, listing)
		origin = origin_raw[0].strip()[11:] if len(origin_raw) > 0 else "N/A"

		# Amazon fulfillment
		amazon_fulfill_raw = re.findall(regex_fulfill, listing)
		amazon_fulfill = True if len(amazon_fulfill_raw) > 0 or seller == "Amazon" else False
		
		# Bundling
		listing_data = {
						 "item_cost": item_cost,
						 "ship_cost": ship_cost,
						 "condition": condition,
						 "seller": seller,
						 "avg_rating": avg_rating,
						 "num_ratings": num_ratings,
						 "pos_feedback": pos_feedback,
						 "desc": desc,
						 "origin": origin,
						 "amazon_fulfill": amazon_fulfill }
		extracted_data.append(listing_data)
		
	return extracted_data
	
def extractLinkInfo(page_content):
	""" Extracts the name of the product and the number of pages of listings:
		{ product_name(str), num_pages(int) }. """
	
	regex_name = "(?<=Buying Choices: ).*?(?=</title>)" # TODO: add extraction of hardcover vs paperback while keeping reliability
	regex_num_pages = "startIndex=(\d+)"

	# Product name
	product_name_raw = re.findall(regex_name, page_content)
	assert len(product_name_raw) > 0, "Could not find product name"
	product_name = product_name_raw[0]
	
	# Number of pages of listings
	num_pages_raw = re.findall(regex_num_pages, page_content)
	assert len(num_pages_raw) > 0, "Could not find number of pages"
	num_pages_raw = [int(num[:-1]) for num in num_pages_raw]
	num_pages = max(num_pages_raw) + 1
	
	# Bundling
	product_info = {
					 "product_name": product_name,
					 "num_pages": num_pages }
	
	return product_info
		
def nextPage(url):
	""" Generates URL of the next page. """
	
	# Locate and increment the startIndex parameter from the URL by 10
	index_location = re.search('=', url).span()
	index_value = str(int(url[index_location[1]:]) + 10)
	
	return url[:index_location[1]] + index_value

def generateURL(user_input, default_tld=".com"):
	""" Generates URL of the listings page from a user input. """

	regex_product_id = "[\dA-Z]{10}"
	regex_tld = "(?<=amazon)(\.com|(\.[a-z]{2})+)"

	# Extract product ID
	product_id_search = re.findall(regex_product_id, user_input)
	if not product_id_search:
		raise Exception("Invalid input: " + user_input)
	else:
		product_id = product_id_search[0]
	
	# Extract TLD, use default if none is found
	tld_search = re.findall(regex_tld, user_input)	
	tld = tld_search[0][0] if len(tld_search) > 0 else default_tld
	
	return "https://amazon{}/gp/offer-listing/{}?startIndex=00".format(tld, product_id)

# Test code for page fetching
'''
url = "https://www.amazon.com/gp/offer-listing/1259587541"#"https://www.amazon.ca/gp/offer-listing/1413006884"#"""https://www.amazon.ca/gp/offer-listing/1285741552?f_new=true"""
headers = {
			"User-Agent": generateUserAgent(),
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Language": "en-US,en;q=0.5",
			"Accept-Encoding": "gzip, deflate, br",
			"DNT": '1',
			"Connection": "close",
			"Upgrade-Insecure-Requests": '1',
			"Cache-Control": "no-cache" }
			
page = requests.get(url, headers=headers).text
extractContent(page)
'''

# Test code for page extraction
'''
with open("testfile", 'r') as f:
	page = f.read()
'''

# Test code for page dumping
'''
with open("testfile2", 'w') as f:
	f.write(page)
'''

# Test code for URL generation
'''
print(generateListingsURL("https://www.amazon.ca/dp/0124077269/140-06439272867759"))
'''
