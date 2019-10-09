from django.forms import ModelForm

from .models import Account, Ledger, Record, Variation


def set_inputs_css_class(form):
    for field in form.visible_fields():
        field.field.widget.attrs['class'] = 'form-control'


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'type', 'parent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_inputs_css_class(self)


class LedgerForm(ModelForm):
    class Meta:
        model = Ledger
        fields = ['name']


class RecordForm(ModelForm):
    class Meta:
        model = Record
        fields = ['date', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_inputs_css_class(self)


class VariationForm(ModelForm):
    class Meta:
        model = Variation
        fields = ['amount', 'account']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_inputs_css_class(self)
