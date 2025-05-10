import urllib.request

webUrl=urllib.request.urlopen('http://127.0.0.1:5000/')

print("result: "+str(webUrl.getCode()))