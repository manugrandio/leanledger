from django.urls import path

from leanledger.records.views import record, records_list, account, accounts_tree

# TODO move to records app
urlpatterns = [
    path('record/<int:pk>/', record, name='record'),
    path('records/', records_list, name='records_list'),
    path('account/<int:pk>/', account, name='account'),
    path('accounts/', accounts_tree, name='accounts_tree'),
]
