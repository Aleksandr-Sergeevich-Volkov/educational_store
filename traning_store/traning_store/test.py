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
""" if cart.delivery:
                order.delivery_sum = cart.delivery_cost



delivery_sum = models.DecimalField(default=0,
                                       max_digits=10,
                                       decimal_places=2)
+ self.delivery_sum """
