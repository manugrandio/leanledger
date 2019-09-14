import json
from collections import namedtuple

from django.shortcuts import render

from leanledger.records.models import Account


Record = namedtuple('Record', 'account, amount')


def records_list(request):
    context = {
        'records': [
            {
                'date': '2019-09-10',
                'debit_variations': [
                    {'account': 'cash', 'amount': 100},
                ],
                'credit_variations': [
                    {'account': 'expenses.book', 'amount': 20},
                    {'account': 'expenses.videogame.mario', 'amount': 40},
                    {'account': 'expenses.videogame.zelda', 'amount': 40},
                ],
            },
            {
                'date': '2019-09-08',
                'debit_variations': [
                    {'account': 'owed', 'amount': 200},
                ],
                'credit_variations': [
                    {'account': 'cash', 'amount': 200},
                ],
            },
        ],
    }
    return render(request, 'records/records_list.html', context)


def accounts_tree(request):
    destination_accounts = Account.objects.destination_accounts()
    origin_accounts = Account.objects.origin_accounts()
    return render(request, 'records/accounts_list.html', {
        'destination_accounts': destination_accounts,
        'origin_accounts': origin_accounts,
    })
