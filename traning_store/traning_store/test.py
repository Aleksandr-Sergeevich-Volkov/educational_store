from decimal import Decimal

x = Decimal('5990.00')
print(x.normalize())
print(x.to_integral())
