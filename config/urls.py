from django.urls import include, path


urlpatterns = [
    path('ledger/', include('leanledger.records.urls')),
]
