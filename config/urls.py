from django.urls import include, path


urlpatterns = [
    path('ledger/', include('leanledger.ledger.urls')),
]
