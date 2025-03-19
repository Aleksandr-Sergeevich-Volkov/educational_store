""" def f_gen(m):
    s = 1
    for n in range(1,m):
        yield n**2 + s
        s += 1
    

a = f_gen(5)
print(a)

for i in a:
    print(i)
 """
import math


""" def prime_num():
    nm = 2
    while True:
        sq = math.ceil(nm**1/2)
        for i in range(2, sq+1):
            if (nm % i) == 0:
                break
            else:
                yield nm
                nm += 1

for num in prime_num():
 	print(num) """
for i in range(2, 1+1):
    print(i)