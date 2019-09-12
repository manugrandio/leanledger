import json
from collections import namedtuple

from django.shortcuts import render

from leanledger.records.models import Account


Record = namedtuple('Record', 'account, amount')


def records_list(request):
    context = {
        'records': [
            Record('cash', 30),
            Record('something', 40),
            Record('whatever', 30),
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
