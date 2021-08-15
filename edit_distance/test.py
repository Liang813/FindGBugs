from collections import Counter

c = Counter(a=4, b=2, c=0, d=-2)
d = Counter(a=3, c=2, b=-2)
c.subtract(d)
print(c)