""" from urllib.parse import urlparse


url = "/robokassa/success/?OutSum=5990.00&InvId=105&SignatureValue=bf829f95ab9f2ad8831532c99fb05d1b&IsTest=1&Culture=ru"
# parsed_url = parse_url(url).query.split('&')
# query = urlparse(url).query.split('&')
query = urlparse(url)
print(query)
params={}
for item in query:
    key, value = item.split('=')
    params[key] = value
print(params) """
