from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView
from django.views import View
import requests

# サイトにアクセスした時に表示する画面までのアクセス
def SearchViewfunc(request):
    if request.method == 'GET':
        print('検索画面の表示!')
        return redirect('search')

# 検索結果画面表示のクラス
class SearchBook(TemplateView):
    template_name = 'result.html'
    context_object_name = 'result'

    def post(self, request, *args, **kwargs):
        # NDL APIのURL
        apiUrl = 'https://ndlsearch.ndl.go.jp/api/opensearch'

        # フォームから入力された検索ワードを取得
        searchword = request.POST.get('searchword', '')

        # APIの検索URLを作成
        searchUrl = f'{apiUrl}?title={searchword}'
        print(f'検索時のURL: {searchUrl}')

        # APIにリクエストを送信
        response = requests.get(searchUrl)

        if response.status_code == 200:
            #レスポンスが正常だった場合
            data = response.json()
        else:
            # エラーハンドリング
            data = {}

        # コンテキストに結果を追加
        context = self.get_context_data()
        context['message'] = data

        # 結果をテンプレートに渡して表示
        return self.render_to_response(context)

