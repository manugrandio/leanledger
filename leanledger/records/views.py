from django.shortcuts import render


def records_list(request):
    return render(request, 'records/records_list.html', {'name': 'hello'})
