from django.urls import path

from .views import (
    ledger_list, ledger_new, ledger_update, ledger_delete,
    record, record_create, record_delete, records,
    account_detail, account_create, account_delete, accounts,
    variation_create, variation_detail, variation_delete,
)


urlpatterns = [
    path('', ledger_list, name='ledger_list'),
    path('new/', ledger_new, name='ledger_new'),
    path('<int:ledger_pk>/delete/', ledger_delete, name='ledger_delete'),
    path('<int:ledger_pk>/update/', ledger_update, name='ledger_update'),
    path('<int:ledger_pk>/record/', records, name='records'),
    path('<int:ledger_pk>/record/new/', record_create, name='record_create'),
    path('<int:ledger_pk>/record/<int:record_pk>/', record, name='record'),
    path('<int:ledger_pk>/record/<int:record_pk>/delete/', record_delete, name='record_delete'),
    path(
        '<int:ledger_pk>/record/<int:record_pk>/variation/new/', variation_create,
        name='variation_create'),
    path(
        '<int:ledger_pk>/record/<int:record_pk>/variation/<int:variation_pk>/', variation_detail,
        name='variation_detail'),
    path(
        '<int:ledger_pk>/record/<int:record_pk>/variation/<int:variation_pk>/delete/',
        variation_delete,
        name='variation_delete'),
    path('<int:ledger_pk>/account/', accounts, name='accounts'),
    path('<int:ledger_pk>/account/create/', account_create, name='account_create'),
    path('<int:ledger_pk>/account/<int:account_pk>/', account_detail, name='account'),
    path('<int:ledger_pk>/account/<int:account_pk>/delete/', account_delete, name='account_delete'),
]
