from django.shortcuts import render, redirect
from django.views.generic import ListView
import requests

# サイトにアクセスした時に表示する画面までのアクセス
def SearchViewfunc(request):
    if request.method == 'GET':
        print('検索画面の表示!')
        return redirect('search')

# 検索結果画面表示のクラス
class SearchBook(ListView):
    def get_postData(request):
        apiUrl = 'https://ndlsearch.ndl.go.jp/api/opensearch'
        if request.method == 'POST':
            input1 = request.POST['searchword']
            print('データを受け取った！')
            print(f'入力されたデータ{input1}')
            searchUrl = apiUrl + '?title=' + '{input1}'
            print(f'検索時のURL: {searchUrl}')
            response = requests.get(searchUrl)
            print(response)
            return render(request, 'result.html', {'message':response.json()})

