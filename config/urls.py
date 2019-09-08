from django.urls import path

from leanledger.records.views import records_list, accounts_tree

urlpatterns = [
    path('records/', records_list, name='records_list'),
    path('accounts/', accounts_tree, name='accounts_tree'),
]
