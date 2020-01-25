from django.urls import path

from .views import (
    ledger_list, ledger_create, ledger_update, ledger_delete,
    record_detail, record_list, record_create,
    account_detail, account_create, account_delete, account_list,
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
    path('<int:ledger_pk>/record/<int:record_pk>/', record_detail, name='record_detail'),

    # Account
    path('<int:ledger_pk>/account/', account_list, name='account_list'),
    path('<int:ledger_pk>/account/create/', account_create, name='account_create'),
    path('<int:ledger_pk>/account/<int:account_pk>/', account_detail, name='account_detail'),
    path('<int:ledger_pk>/account/<int:account_pk>/delete/', account_delete, name='account_delete'),
]
