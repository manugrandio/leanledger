import json
from collections import namedtuple

from django.shortcuts import render

from leanledger.records.models import Account, Record


def records_list(request):
    context = {'records': Record.objects.all()}
    return render(request, 'records/records_list.html', context)


def account(request, pk):
    account = Account.objects.get(pk=pk)  # TODO replace for get_or_404
    return render(request, 'records/account.html', {'account': account})


def accounts_tree(request):
    destination_accounts = Account.objects.destination_accounts()
    origin_accounts = Account.objects.origin_accounts()
    return render(request, 'records/accounts_list.html', {
        'destination_accounts': destination_accounts,
        'origin_accounts': origin_accounts,
    })
