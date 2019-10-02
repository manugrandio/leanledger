from django.forms import ModelForm

from .models import Account, Ledger


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'type', 'parent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class LedgerForm(ModelForm):
    class Meta:
        model = Ledger
        fields = ['name']
