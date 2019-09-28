import json
from collections import namedtuple

from django.shortcuts import render

from leanledger.records.models import Ledger, Account, Record


def ledgers(request):
    ledgers = Ledger.objects.all()  # TODO get just the user's ledgers
    return render(request, 'records/ledger_list.html', {'ledgers': ledgers})


def record(request, ledger_pk, record_pk):
    record = Record.objects.get(pk=record_pk)  # TODO replace for get_or_404
    return render(request, 'records/record.html', {'record': record, 'ledger_pk': ledger_pk})


def records(request, ledger_pk):
    context = {'records': Record.objects.all(), 'ledger_pk': ledger_pk}
    return render(request, 'records/records_list.html', context)


def account(request, ledger_pk, account_pk):
    account = Account.objects.get(pk=account_pk)  # TODO replace for get_or_404
    return render(request, 'records/account.html', {'account': account, 'ledger_pk': ledger_pk})


def accounts(request):
    destination_accounts = Account.objects.destination_accounts()
    origin_accounts = Account.objects.origin_accounts()
    return render(request, 'records/accounts_list.html', {
        'destination_accounts': destination_accounts,
        'origin_accounts': origin_accounts,
    })
