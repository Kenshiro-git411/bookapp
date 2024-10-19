from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.http import HttpResponse
from urllib.parse import quote
import xml.etree.ElementTree as ET
import json, xmltodict
import requests
from django.urls import reverse_lazy


# 最初にサイトにアクセスした時に表示する画面までのアクセス
def SearchViewfunc(request):
    if request.method == 'GET':
        print('検索画面の表示!')
        return render(request, 'search.html', {})
    # 他のメソッドに対する処理も追加
    # print('HttpResponse前')
    # return HttpResponse('このメソッドはサポートされていません。', status=405)

# ログインもしくはサインアップ後の検索画面表示
def SearchAfterViewfunc(request):
    if request.method == 'GET':
        print('ログインもしくはサインアップ後の検索画面表示')
        return render(request, 'searchafter.html', {})

# 検索結果画面表示のクラス
class SearchBook(TemplateView):
    template_name = 'result.html'
    context_object_name = 'result'

    def post(self, request, *args, **kwargs):
        print("SearchGBookクラス-post関数の始まり")
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
            data = json.loads(data)

        else:
            # エラーハンドリング
            data = {}

        # コンテキストに結果を追加
        context = self.get_context_data()
        context['message'] = data
        book_list = []

        for item in data["rss"]["channel"]["item"]:
            book_dict = {}
            for key, value in item.items():
                if key == "title" or key == "link" or key == "description":
                    book_dict[key] = value
                    print("-------------------------------------------------------------------------")
                    print(f'キー: {key}')
                    print(f'バリュー: {value}')
                    print("-------------------------------------------------------------------------")

            book_list.append(book_dict)
        print(book_list)
        context.update({
            "book_list": book_list
        })

        # 結果をテンプレートに渡して表示
        return self.render_to_response(context)


# サインアップ処理
class Signup(CreateView):
    template_name = 'signup.html'
    model = User
    fields = ['username', 'password'] # 必要なフィールドを指定
    
    def form_valid(self, form):
        # フォームが有効な場合の処理
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        try:
            # 新しいユーザーを作成
            user = User.objects.create_user(username=username, password=password)
            print('登録の重複はありません。登録処理を実行済みです。')

            # 自動的にログイン
            login(self.request, user)

            # リダイレクト先を指定
            return redirect('searchafter')

        except IntegrityError:
            print('登録の重複があります。登録できませんでした。')
            form.add_error('username', 'このユーザーはすでに登録されています')
            return self.form_invalid(form)

    def form_invalid(self, form):
        # フォームが無効な場合の処理
        return render(self.request, self.template_name, {'form': form})


# ログイン処理
class UserLogin(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True  # 既にログインしているユーザーはリダイレクト
    next_page = reverse_lazy('') # リダイレクト先

    def form_valid(self, form):
        try:
            # userのログインが成功する場合
            user = form.get_user()
            print('ユーザーが登録されていることを確認できました。')
            login(self.request, user) # ログイン処理
            return redirect('searchafter')
        
        except IntegrityError:
            # userのログインが失敗する場合
            print('そのユーザーは登録されておりません。')
            return self.form_invalid(form)

    def form_invalid(self, form):
        print('ユーザーが登録されていることを確認できませんでした')
        return render(self.request, self.template_name, {'form': form})
    
class Logout(LogoutView):
    template_name = 'logout.html' #ログアウト後に表示するテンプレート
    