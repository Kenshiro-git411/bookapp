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
        def modify_date(pre_dates):
            # print(pre_dates)
            # print(type(pre_dates))

            # 正規表現のパターンを作成
            pattern = r'\b(\d{4})\s*[-.,]\s*(\d{1,2})\s*[-.,]\s*(\d{1,2})\b|\b(\d{4})\s*[-.,]\s*(\d{1,2})\b|\b(\d{4})\b'

            # 全角を半角に変換するための変換テーブルを作成
            fullwidth = "１２３４５６７８９０．"
            halfwidth = "1234567890."

            # 変換テーブルを使って変換
            translation_table = str.maketrans(fullwidth, halfwidth)
            # print(f'translation_table内容: {translation_table}')
            pre_dates = pre_dates.translate(translation_table)

            # 書き換え関数
            def convert_date(match):
                if match.group(1) and match.group(2) and match.group(3):  # YYYY-MM-DD形式
                    year, month, day = match.group(1), match.group(2), match.group(3)
                    return f"{int(year)}年{int(month)}月{int(day)}日"
                elif match.group(4) and match.group(5):  # YYYY-MM形式
                    year, month = match.group(4), match.group(5)
                    return f"{int(year)}年{int(month)}月"
                elif match.group(6):  # YYYY形式
                    year = match.group(6)
                    return f"{int(year)}年"
                else:
                    year = None
                    return year

            # 日付を変換
            converted_dates = re.sub(pattern, convert_date, pre_dates) 

            # 日付の正しい表記確認
            pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日|\b(\d{4})年(\d{1,2})月|\b(\d{4})年'
            match = re.match(pattern, converted_dates)
            if match:
                print(f"適切な表記に変換済み: {converted_dates}")
                # print("Groups:", match.groups())
                return converted_dates
            else:
                print(f"表記が不正: {converted_dates}")
                converted_dates = "N/A"
                return converted_dates
        
        def pub_date(pre_dates):
            # 月の名前を数字に変換する辞書
            month_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            # 日付と月を抽出
            month = month_map[pre_dates[2]]
            year = pre_dates[3]

            return f'{year}年{month}月'

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
                    # 出版社
                        key = "publisher"
                        print(f'value: {value}')
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
                        converted_dates = modify_date(value)
                        # 結果を表示
                        # for original, converted in zip(value, converted_dates):
                        #     print(f"{original} -> {converted}")
                        book_dict[key] = converted_dates
                        print("-------------------------------------------------------------------------")
                        print(f'キー: {key}')
                        print(f'バリュー: {converted_dates}')
                        print("-------------------------------------------------------------------------")

                # 出版社をはじめからjsonで持っていないデータの処理
                if "publisher" not in book_dict:
                    key = "publisher"
                    value = "N/A"
                    book_dict[key] = value
                    print("-------------------------------------------------------------------------")
                    print(f'キー: {key}')
                    print(f'バリュー: {value}')
                    print("-------------------------------------------------------------------------")
                    # print(f'出版社がないdict: {book_dict}')

                # 出版年に空白またNoneが入っているデータの処理
                if "publish_year" not in book_dict or book_dict["publish_year"] == "N/A":
                    key = "publish_year"
                    find_key = "pubDate"
                    tmp_pub_dates = data["rss"]["channel"]["item"][0].get(find_key)
                    # print(f'tmp_pub_dates: {tmp_pub_dates}')
                    tmp_pub_dates = tmp_pub_dates.split()
                    # print(f'tmp_pub_dates: {tmp_pub_dates}')
                    value = pub_date(tmp_pub_dates)
                    book_dict[key] = value

                print(f'1つのbook_dictの内容: {book_dict}')
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
            return redirect('api:searchafter')

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

def Detailfunc(request):
    # requestの中身にpkが振られているから、それに該当するものを表示させる。
    # print(request.__dict__)
    # print(vars(request))
    json_str = request.body
    json_data = json.loads(json_str)
    print(json_data)
    # if request.method == 'GET':
    return redirect('detail')


