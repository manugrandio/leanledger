from django.urls import path

from leanledger.records.views import ledgers, record, records, account, accounts

# TODO move to records app
urlpatterns = [
    path('ledger/', ledgers, name='ledgers'),
    path('ledger/<int:ledger_pk>/record/', records, name='records'),
    path('ledger/<int:ledger_pk>/record/<int:record_pk>/', record, name='record'),
    path('ledger/<int:ledger_pk>/account/', accounts, name='accounts'),
    path('ledger/<int:ledger_pk>/account/<int:account_pk>/', account, name='account'),
]
