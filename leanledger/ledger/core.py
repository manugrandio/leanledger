DEBIT = 'debit'
CREDIT = 'credit'


def record_is_balanced(record):
    debit_sum, credit_sum = 0, 0
    for variation in record.variations.all():
        amount = abs(variation.amount)
        if variation.type == DEBIT:
            debit_sum += amount
        else:
            credit_sum += amount
    return debit_sum == credit_sum
