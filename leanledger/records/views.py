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
    accounts = Account.objects.filter(parent=None)
    return render(request, 'records/accounts_tree.html', {'accounts': accounts})
