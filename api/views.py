from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponse
from urllib.parse import quote
import xml.etree.ElementTree as ET
import json, xmltodict
import requests

# サイトにアクセスした時に表示する画面までのアクセス
def SearchViewfunc(request):
    if request.method == 'GET':
        print('検索画面の表示!')
        return render(request, 'search.html', {})
    # 他のメソッドに対する処理も追加
    # print('HttpResponse前')
    # return HttpResponse('このメソッドはサポートされていません。', status=405)

# 検索結果画面表示のクラス
class SearchBook(TemplateView):
    template_name = 'result.html'
    context_object_name = 'result'

    def post(self, request, *args, **kwargs):
        print("SearchGBook関数の始まり")
        # NDL APIのURL
        apiUrl = 'https://ndlsearch.ndl.go.jp/api/opensearch'

        # フォームから入力された検索ワードを取得
        searchword = request.POST.get('searchword', '')

        # フォームから入力された検索ワードをエンコードする
        encoding_searchword = quote(searchword)
        # print(f'encode後検索ワード: {encoding_searchword}')

        # APIの検索URLを作成
        searchUrl = f'{apiUrl}?title={encoding_searchword}'
        # print(f'検索時のURL: {searchUrl}')

        # APIにリクエストを送信
        response = requests.get(searchUrl)
        # print(response)

        #レスポンスが正常だった場合
        if response.status_code == 200:
            xml_data = response.content
            # print(xml_data)

            # XMLデータをパースする
            root = xmltodict.parse(xml_data)
            # print(root)

            # 辞書をJSON形式に変換
            data = json.dumps(root, ensure_ascii=False, indent=2)

            # JSONデータを辞書に変換
            # data = json.loads(data)

        else:
            # エラーハンドリング
            data = {}

        # コンテキストに結果を追加
        context = self.get_context_data()
        context['message'] = data

        # for item in data['rss']['channel']['item']:
        #     print(item['title'],item['author'])

        # 結果をテンプレートに渡して表示
        return self.render_to_response(context)

