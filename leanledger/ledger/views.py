import json
from collections import namedtuple

from django.shortcuts import render

from .models import Ledger, Account, Record


def ledgers(request):
    ledgers = Ledger.objects.all()  # TODO get just the user's ledgers
    return render(request, 'ledger/ledger_list.html', {'ledgers': ledgers})


def ledger_new(request):
    if request.POST:
        return render(request, 'ledger/ledger_created.html', {'name': request.POST['name']})
    else:
        return render(request, 'ledger/ledger_new.html')


def record(request, ledger_pk, record_pk):
    record = Record.objects.get(pk=record_pk)  # TODO replace for get_or_404
    return render(request, 'ledger/record.html', {'record': record, 'ledger_pk': ledger_pk})


def records(request, ledger_pk):
    context = {'records': Record.objects.all(), 'ledger_pk': ledger_pk}
    return render(request, 'ledger/records_list.html', context)


def account(request, ledger_pk, account_pk):
    account = Account.objects.get(pk=account_pk)  # TODO replace for get_or_404
    return render(request, 'ledger/account.html', {'account': account, 'ledger_pk': ledger_pk})


def accounts(request):
    destination_accounts = Account.objects.destination_accounts()
    origin_accounts = Account.objects.origin_accounts()
    return render(request, 'ledger/accounts_list.html', {
        'destination_accounts': destination_accounts,
        'origin_accounts': origin_accounts,
    })
