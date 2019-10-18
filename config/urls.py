from django.shortcuts import redirect
from django.urls import include, path


urlpatterns = [
    path('', lambda r: redirect('ledger_list'), name='root'),
    path('ledger/', include('leanledger.ledger.urls')),
]
