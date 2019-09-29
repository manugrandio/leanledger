from django.forms import ModelForm

from .models import Ledger


class LedgerForm(ModelForm):
    class Meta:
        model = Ledger
        fields = ['name']
