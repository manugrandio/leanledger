from django.urls import path

from leanledger.records.views import records_list

urlpatterns = [
    path('records/', records_list, name='records_list'),
]
