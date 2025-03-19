
import math

""" def prime_num(limit):
    nm = 2
    while nm<limit:
        #sq = math.ceil(nm**1/2)
        #for i in range(2, sq+1):
        if all((nm % i) != 0 for i in range(2,int(nm**0.5)+1)):
            yield nm
        nm += 1

for num in prime_num(50):
    print(num)    """
for i in range(2,int(29**0.5)+1):
    print(i,int(29**0.5))

""" def find_prime():
    num = 1
    while True:
        if num > 1:
            for i in range(2, num):
                if (num % i) == 0:
                    break
        else:
            yield num
            num += 1

for ele in find_prime():
    print(ele) """
""" def prime_numbers(limit):
    num = 2
    while num<=limit:
        if all(num % i != 0 for i in range(2, int(num ** 0.5) + 1)):
            yield num
        num += 1

for prime in prime_numbers(682739):
    print(prime)  """
