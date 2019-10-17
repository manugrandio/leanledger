import json
from collections import namedtuple

from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import AccountForm, LedgerForm, RecordForm, VariationForm
from .models import Ledger, Account, Record, Variation


def ledger_list(request):
    ledgers = Ledger.objects.all()  # TODO get just the user's ledgers
    return render(request, 'ledger/ledger_list.html', {'ledgers': ledgers})


def ledger_create(request):
    def get_user():  # TODO replace for just `request.user` when auth is set up
        return User.objects.first() if isinstance(request.user, AnonymousUser) else request.user

    form = LedgerForm(request.POST or None)
    if request.method == 'POST':
        form = LedgerForm(request.POST)
        if form.is_valid():
            ledger = form.save(commit=False)
            ledger.user = get_user()
            ledger.save()
            return redirect(reverse('ledger_list'))
        # TODO handle errors (and also in template)
        return render(request, 'ledger/ledger_create.html', {'form': form})
    return render(request, 'ledger/ledger_create.html', {'form': form})


def ledger_update(request, ledger_pk):
    ledger = Ledger.objects.get(pk=ledger_pk)
    if request.method == 'POST':
        form = LedgerForm(request.POST, instance=ledger)
        if form.is_valid():
            form.save()
            return redirect(reverse('ledger_list'))
        # TODO handle errors (and also in template)
    else:
        form = LedgerForm(instance=ledger)
    return render(request, 'ledger/ledger_update.html', {'form': form})


def ledger_delete(request, ledger_pk):
    ledger = Ledger.objects.get(pk=ledger_pk)
    if request.method == 'POST':
        ledger.delete()
        return redirect(reverse('ledger_list'))
    else:
        return render(request, 'ledger/ledger_delete_confirmation.html', {'ledger': ledger})


def record(request, ledger_pk, record_pk):
    ledger = Ledger.objects.get(pk=ledger_pk)
    record = Record.objects.get(pk=record_pk)  # TODO replace for get_or_404
    return render(request, 'ledger/record.html', {'record': record, 'ledger': ledger})


def record_list(request, ledger_pk):
    ledger = Ledger.objects.get(pk=ledger_pk)
    records = Record.objects.filter(ledger=ledger_pk).order_by('-date')
    context = {'records': records, 'ledger': ledger}
    return render(request, 'ledger/records_list.html', context)


def record_create(request, ledger_pk):
    ledger = Ledger.objects.get(pk=ledger_pk)
    form = RecordForm(request.POST or None)
    if form.is_valid():
        record = form.save(commit=False)
        record.ledger = ledger
        record.save()
        return redirect(reverse('record', args=[ledger.pk, record.pk]))
        # TODO handle form errors
    return render(request, 'ledger/record_create.html', context={
        'form': form,
        'ledger': ledger,
    })


def record_delete(request, ledger_pk, record_pk):
    ledger = Ledger.objects.get(pk=ledger_pk)
    record = Record.objects.get(pk=record_pk)
    if request.method == 'POST':
        record.delete()
        return redirect(reverse('record_list', args=[ledger_pk]))
    return render(request, 'ledger/record_delete.html', {
        'record': record,
        'ledger': ledger,
    })



def account_detail(request, ledger_pk, account_pk):
    ledger = Ledger.objects.get(pk=ledger_pk)
    account = Account.objects.get(pk=account_pk)  # TODO replace for get_or_404
    return render(request, 'ledger/account.html', {'account': account, 'ledger': ledger})


def accounts(request, ledger_pk):
    ledger = Ledger.objects.get(pk=ledger_pk)
    destination_accounts = Account.objects.destination_accounts(ledger_pk)
    origin_accounts = Account.objects.origin_accounts(ledger_pk)
    return render(request, 'ledger/accounts_list.html', {
        'destination_accounts': destination_accounts,
        'origin_accounts': origin_accounts,
        'ledger': ledger,
    })


def account_create(request, ledger_pk):
    ledger = Ledger.objects.get(pk=ledger_pk)
    parent = request.GET.get('parent')
    form_kwargs = {'initial': {'parent': parent}} if parent is not None else {}
    form = AccountForm(request.POST or None, **form_kwargs)
    if request.method == 'POST':
        if form.is_valid():
            account = form.save(commit=False)
            account.ledger = Ledger.objects.get(pk=ledger_pk)
            account.type = account.parent.type
            account.save()
            return redirect(reverse('accounts', args=[account.ledger.pk]))
        # TODO handle form errors
    return render(request, 'ledger/account_create.html', {'form': form, 'ledger': ledger})


def account_delete(request, ledger_pk, account_pk):
    ledger = Ledger.objects.get(pk=ledger_pk)
    account = Account.objects.get(pk=account_pk)
    if request.method == 'POST':
        account.delete()
        return redirect(reverse('accounts', args=[ledger.pk]))
    return render(request, 'ledger/account_delete.html', {
        'ledger': ledger,
        'account': account,
    })


def variation_detail(request, ledger_pk, record_pk, variation_pk):
    variation = Variation.objects.get(pk=variation_pk)
    return render(request, 'ledger/variation_detail.html', {
        'variation': variation,
        'record_pk': record_pk,
        'ledger_pk': ledger_pk,
    })


def variation_create(request, ledger_pk, record_pk):
    form = VariationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            variation = form.save(commit=False)
            variation.record = Record.objects.get(pk=record_pk)
            variation.save()
            return redirect(reverse('record', args=[ledger_pk, record_pk]))
        # TODO handle form errors
    return render(request, 'ledger/variation_create.html', {
        'form': form,
        'record_pk': record_pk,
        'ledger_pk': ledger_pk
    })


def variation_delete(request, ledger_pk, record_pk, variation_pk):
    if request.method != 'POST':
        return HttpResponseForbidden('Method not allowed')
    Variation.objects.get(pk=variation_pk).delete()
    return redirect(reverse('record', args=[ledger_pk, record_pk]))
