from django.urls import path

from leanledger.records.views import ledgers_list, record, records_list, account, accounts_tree

# TODO move to records app
urlpatterns = [
    path('ledger/', ledgers_list, name='ledgers_list'),
    path('ledger/<int:ledger_pk>/', records_list, name='records_list'),
    path('record/<int:pk>/', record, name='record'),
    path('account/<int:pk>/', account, name='account'),
    path('accounts/', accounts_tree, name='accounts_tree'),
]
