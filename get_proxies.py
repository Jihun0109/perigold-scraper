import requests,re
from scrapy.http import TextResponse
from scrapy.utils.response import open_in_browser

url = "https://www.sslproxies.org/"

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36',}
r = requests.get(url)
html = requests.get(url, headers=headers).text

items = re.findall('\d+\.\d+.\d+\.\d+</td><td>\d+</td>', html)
items = [x.replace('</td>','') for x in items]
items = set(items)

with open('proxies.txt', 'w') as the_file:
	for item in items:
		ip,port = item.split("<td>")
		print (ip, ":", port)
		the_file.write(ip+":"+port+'\n')

