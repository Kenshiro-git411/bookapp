from django.shortcuts import render
from django.views.generic import ListView
import requests

class SearchBook(ListView):
    # template_name = 'result.html'
    def get(self, request, *args, **kwargs):
        response = requests.get("https://ndlsearch.ndl.go.jp/api/opensearch")

        return render(request, 'result.html', {'message': '検証'})
