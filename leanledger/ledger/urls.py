from django.urls import path

from .views import (
    ledgers, ledger_new, ledger_update, ledger_delete, record, record_create,
    records, account, account_create, accounts
)


urlpatterns = [
    path('', ledgers, name='ledgers'),
    path('new/', ledger_new, name='ledger_new'),
    path('<int:ledger_pk>/delete/', ledger_delete, name='ledger_delete'),
    path('<int:ledger_pk>/update/', ledger_update, name='ledger_update'),
    path('<int:ledger_pk>/record/', records, name='records'),
    path('<int:ledger_pk>/record/new/', record_create, name='record_create'),
    path('<int:ledger_pk>/record/<int:record_pk>/', record, name='record'),
    path('<int:ledger_pk>/account/', accounts, name='accounts'),
    path('<int:ledger_pk>/account/create/', account_create, name='account_create'),
    path('<int:ledger_pk>/account/<int:account_pk>/', account, name='account'),
]
