from .models import Variation  # TODO do not import from models.py


def record_is_balanced(record):
    debit_sum, credit_sum = 0, 0
    for variation in record.variations:
        if variation.type == Variation.DEBIT:
            debit_sum += variation.amount
        else:
            credit_sum += variation.amount
    return debit_sum == credit_sum
