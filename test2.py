import re
import os
import threading
import time
import requests
import urllib2
import urlparse

#==============================================================
start_time = time.time()

scribdId = raw_input("scribdLink: ").split("/")[-2]
print("Found [scribdId] => %s" %scribdId)
#print("Try to access: https://www.scribd.com/doc/%s..." %scribdId)
urlContent = requests.get("https://www.scribd.com/doc/" + scribdId).text
scribdTitle = re.search('"title":"(.*?)",', urlContent).group(1)
accessKey = re.search('"access_key":"key-(.*?)",', urlContent).group(1)
print("Found [scribdTitle] => %s" %scribdTitle)
print("Found [accessKey] => %s" %accessKey)
if not os.path.exists(scribdTitle):
    os.makedirs(scribdTitle)
#==============================================================
#print("Try to access: https://www.scribd.com/fullscreen/%s?access_key=key-%s..." %(scribdId,accessKey))
urlContent = requests.get("https://www.scribd.com/fullscreen/%s?access_key=key-%s" %(scribdId,accessKey)).text
assetPrefix = re.search('docManager.assetPrefix = "(.*?)";', urlContent).group(1)
print("Found [assetPrefix] => %s" %assetPrefix)
regex = "https://html[0-9]-f.scribdassets.com/%s/pages/[0-9]+-[0-9a-z]+.jsonp" %assetPrefix
pageUrls = re.findall(regex,urlContent)
print("Found %i pages to load..." %len(pageUrls))
#===============================================================

def bubble(bad_list):
    length = len(bad_list) - 1
    sorted = False

    while not sorted:
        sorted = True
        for i in range(length):
            if int(re.search('/images/(.*?)-',bad_list[i]).group(1)) > int(re.search('/images/(.*?)-',bad_list[i+1]).group(1)):
                #print("if %i > %s"%(re.search('/images/(.*?)-',bad_list[i]).group(1),re.search('/images/(.*?)-',bad_list[i+1]).group(1)))
                sorted = False
                bad_list[i], bad_list[i+1] = bad_list[i+1], bad_list[i]

def fetch_url(url):
    global urlContent
    html = requests.get(url).text
    urlContent = urlContent + html

threads = [threading.Thread(target=fetch_url, args=(url,)) for url in pageUrls]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

#=============================================================
regex = "http://html.scribd.com/%s/images/[0-9]+-[0-9a-z]+.(?:png|jpg)" %assetPrefix
imgUrls = re.findall(regex, urlContent)  		#find all imgs
imgUrls = list(set(imgUrls))	#remove duplicates
print("Found %i images to download..." %len(imgUrls))
bubble(imgUrls)     #reorder
count = 0
for imgUrl in imgUrls:
	try:
		count += 1
		print "[%i/%i] %s" %(count,len(imgUrls),imgUrl)
		imgData = urllib2.urlopen(imgUrl).read()
		imgName = urlparse.urlsplit(imgUrl)[2].split("/")[-1]
		outdir = os.getcwd() + "/" + scribdTitle + "/" + imgName   #("".join([c for c in scribdTitle if c.isalpha() or c.isdigit() or c==' ']).rstrip())
		#print outdir
		output = open(outdir,'wb')
		output.write(imgData)
		output.close()
	except (RuntimeError, TypeError, NameError) as e:
		print e

print("--- %s seconds ---" % (time.time() - start_time))
#=============================================================
