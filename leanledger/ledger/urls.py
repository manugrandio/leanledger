from django.urls import path

from .views import ledgers, ledger_new, record, records, account, accounts


urlpatterns = [
    path('', ledgers, name='ledgers'),
    path('new/', ledger_new, name='ledger_new'),
    path('<int:ledger_pk>/record/', records, name='records'),
    path('<int:ledger_pk>/record/<int:record_pk>/', record, name='record'),
    path('<int:ledger_pk>/account/', accounts, name='accounts'),
    path('<int:ledger_pk>/account/<int:account_pk>/', account, name='account'),
]
