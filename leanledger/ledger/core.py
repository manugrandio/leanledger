DEBIT = 'debit'
CREDIT = 'credit'


def record_is_balanced(record):
    debit_sum, credit_sum = 0, 0
    for variation in record.variations.all():
        if variation.type == DEBIT:
            debit_sum += variation.amount
        else:
            credit_sum += variation.amount
    return debit_sum == credit_sum
