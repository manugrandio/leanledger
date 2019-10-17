from django.urls import path

from .views import (
    ledger_list, ledger_create, ledger_update, ledger_delete,
    record, record_create, record_delete, record_list,
    account_detail, account_create, account_delete, account_list,
    variation_create, variation_detail, variation_delete,
)


urlpatterns = [
    # Ledger
    path('', ledger_list, name='ledger_list'),
    path('create/', ledger_create, name='ledger_create'),
    path('<int:ledger_pk>/delete/', ledger_delete, name='ledger_delete'),
    path('<int:ledger_pk>/update/', ledger_update, name='ledger_update'),

    # Record
    path('<int:ledger_pk>/record/', record_list, name='record_list'),
    path('<int:ledger_pk>/record/create/', record_create, name='record_create'),
    path('<int:ledger_pk>/record/<int:record_pk>/', record, name='record'),
    path('<int:ledger_pk>/record/<int:record_pk>/delete/', record_delete, name='record_delete'),

    # Account
    path('<int:ledger_pk>/account/', account_list, name='account_list'),
    path('<int:ledger_pk>/account/create/', account_create, name='account_create'),
    path('<int:ledger_pk>/account/<int:account_pk>/', account_detail, name='account'),
    path('<int:ledger_pk>/account/<int:account_pk>/delete/', account_delete, name='account_delete'),

    # Variation
    path(
        '<int:ledger_pk>/record/<int:record_pk>/variation/create/', variation_create,
        name='variation_create'),
    path(
        '<int:ledger_pk>/record/<int:record_pk>/variation/<int:variation_pk>/', variation_detail,
        name='variation_detail'),
    path(
        '<int:ledger_pk>/record/<int:record_pk>/variation/<int:variation_pk>/delete/',
        variation_delete,
        name='variation_delete'),
]
