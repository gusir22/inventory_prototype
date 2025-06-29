from decimal import Decimal, ROUND_HALF_UP

def round_money(value):
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
