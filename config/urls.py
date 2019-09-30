from django.shortcuts import redirect
from django.urls import include, path


urlpatterns = [
    path('', lambda r: redirect('ledgers'), name='root'),
    path('ledger/', include('leanledger.ledger.urls')),
]
