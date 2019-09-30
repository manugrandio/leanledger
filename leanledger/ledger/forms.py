from django.forms import ModelForm

from .models import Account, Ledger


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'type', 'parent']


class LedgerForm(ModelForm):
    class Meta:
        model = Ledger
        fields = ['name']
