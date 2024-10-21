from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse
from urllib.parse import quote
import xml.etree.ElementTree as ET
import json, xmltodict
import requests
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from bs4 import BeautifulSoup
import re

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

        # カンマごとでリストの格納位置を変える関数(最初のデータの持ち方が悪い場合、正しく表示できない。['小林','正一']など)
        def modify_string(value):
            # jsonのauthorに値が何も入っていない場合
            if not value:
                pass
            # jsonのauthorに値が入っている場合
            else:
                # print(f'Type of value: {type(value)}')
                # print(value)
                valList = value.split(',',2)
                # print(valList)
                valList = [st for st in valList if ',' not in st]
                # print(f'valList:{valList[0]}')
                author_name = ''.join(valList[:2])
                return author_name

        # 論文雑誌名とページ数を抽出する
        def modify_dict(dict):
            # print("modify_dict関数")
            # print(type(dict))
            data = re.split(r'[：, ,/,]', dict)
            data = data[1:len(data)]
            re_dict = {
                "thesis": data[0], # 掲載論文名
                "page": data[len(data)-1] # 論文ページ(始まり～終わり)
            }
            # print(re_dict)
            # print(data)
            return re_dict
        
        # 出版年を統一した表記に変形
        def modify_year(year):
            pattern = r'\b(\d{4}-\d{2}-\d{2})\b|\b(\d{4}\.\d{1,2})\b|\b(20\d{2})\b' 
            print(year)
            matches = re.findall(pattern, year)
            extracted_dates = [match[0] if match[0] else match[1] for match in matches]
            print('抽出した日付や年:', extracted_dates)
            return extracted_dates

        # データ内容確認コード（※使用しないときはコメントアウトにしておく）
        # i = 0
        # for item in data["rss"]["channel"]["item"]:
        #     if i < 10:
        #         print(item)
        #         i += 1
        #     else:
        #         break


        i = 0
        for item in data["rss"]["channel"]["item"]:
            book_dict = {}
            if i < 10:
                for key, value in item.items():
                    if key == "title" or key == "link":
                    # タイトル
                        book_dict[key] = value
                        print("-------------------------------------------------------------------------")
                        print(f'キー: {key}')
                        print(f'バリュー: {value}')
                        print("-------------------------------------------------------------------------")

                    elif key == "dc:creator":
                    # 著者・編者
                        key = "author"
                        # authorは、リストの最後にもっている値が正式にNDLでも使用されてるっぽい。
                        # print(f'value:{value}')
                        authorString = modify_string(value)
                        # print(authorString)
                        book_dict[key] = authorString
                        print("-------------------------------------------------------------------------")
                        print(f'キー: {key}')
                        print(f'バリュー: {authorString}')
                        print("-------------------------------------------------------------------------")

                    elif key == "category":
                    # 資料種別
                        # valueがリストになっている。リストの1つ目が資料種別、2つ目が資料形態？
                        val = value[0]
                        book_dict[key] = val
                        print("-------------------------------------------------------------------------")
                        print(f'キー: {key}')
                        print(f'バリュー: {val}')
                        print("-------------------------------------------------------------------------")

                    elif key == "dc:publisher":
                        key = "publisher"
                        book_dict[key] = value
                        print("-------------------------------------------------------------------------")
                        print(f'キー: {key}')
                        print(f'バリュー: {value}')
                        print("-------------------------------------------------------------------------")

                    elif key == "dc:description":
                    # 雑誌名(key=thesis)、ページ数(key=page)
                        # print(value)
                        # print(type(value))
                        # print(f'descriptionのbook_dict:{book_dict}')
                        if "記事" in book_dict.values():
                            # print('dc:descriptionの表示')
                            # print(f'バリュー: {value}')
                            tmp_dict = modify_dict(value)

                            # 雑誌名とページ数が1つの辞書に入っているのでひとつずつ抽出
                            for key, val in tmp_dict.items():
                                # print(f'tmp_dict: {tmp_dict}')
                                book_dict[key] = val
                                print("-------------------------------------------------------------------------")
                                print(f'キー: {key}')
                                print(f'バリュー: {val}')
                                print("-------------------------------------------------------------------------")
                        else:
                            pass

                    elif key == "dcterms:issued":
                    # 出版年(key=publish_year)
                        key = "publish_year"
                        value = modify_year(value)
                        book_dict[key] = value
                        print("-------------------------------------------------------------------------")
                        print(f'キー: {key}')
                        print(f'バリュー: {value}')
                        print("-------------------------------------------------------------------------")

                # print(f'1つのbook_dictの内容:{book_dict}')
                book_list.append(book_dict)
                print('1セット終了です。')

                i += 1
            else:
                break
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

    def form_valid(self, form):
        try:
            # userのログインが成功する場合
            user = form.get_user()
            print('ユーザーが登録されていることを確認できました。')
            login(self.request, user) # ログイン処理
            return redirect('api:searchafter')
        
        except IntegrityError:
            # userのログインが失敗する場合
            print('そのユーザーは登録されておりません。')
            return self.form_invalid(form)

    def form_invalid(self, form):
        print('ユーザーが登録されていることを確認できませんでした')
        return render(self.request, self.template_name, {'form': form})
    
class UserLogout(LogoutView):
    template_name = 'logout.html' #ログアウト後に表示するテンプレート
    # next_page = reverse_lazy('')

    def get(self, request, *args, **kwargs):
        # logout(request)
        print("ログアウトします")
        return super.get(*args, **kwargs)

def Detailfunc(request):
    # requestの中身にpkが振られているから、それに該当するものを表示させる。
    # print(request.__dict__)
    # print(vars(request))
    json_str = request.body
    json_data = json.loads(json_str)
    print(json_data)
    # if request.method == 'GET':
    return redirect('detail')