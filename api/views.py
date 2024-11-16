from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import TemplateView, CreateView, FormView
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
from django.views.generic import ListView
from django.views import View
from .models import Book
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Type, Author, Publisher, Magazine, Book
from .forms import SearchForm, LoginForm, UserCreateForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import loads, dumps, SignatureExpired, BadSignature
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import Http404, HttpResponseBadRequest

# 最初にサイトにアクセスした時に表示する画面までのアクセス
def SearchViewfunc(request):
    form = SearchForm()

    print('検索画面の表示!')
    # sessionに保存されている前回の検索ワードを取り出してくる（SearchBookクラスにてセッションは取得済み）
    searchword = request.session.get("searchword", "")
    book_list = request.session.get("book_list", "")

    # print(book_list)
    return render(request, 'search.html', {
        "search_word": searchword,
        "form": form
    })

    # 他のメソッドに対する処理も追加
    # print('HttpResponse前')
    # return HttpResponse('このメソッドはサポートされていません。', status=405)


# 検索結果画面表示のクラス
class SearchBook(TemplateView, FormView):
    template_name = 'result.html'
    context_object_name = 'result'
    form_class = SearchForm

    def form_valid(self,request, *args, **kwargs):
        print("SearchGBookクラス-post関数の始まり")
        # NDL APIのURL
        apiUrl = 'https://ndlsearch.ndl.go.jp/api/opensearch'

        # フォームから入力された検索ワードを取得
        searchword = request.cleaned_data.get('searchword', '')
        print(searchword)

        # 検索ワードをsessionに保存する(検索画面の入力箇所へのセッション適用)
        self.request.session["searchword"] = searchword

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
        # try:
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

        # レスポンスが異常だった場合
        else:
            # エラーハンドリング
            data = {}

        # コンテキストに結果を追加
        context = self.get_context_data()
        context['message'] = data
        book_list = []

        # [著者に関するデータ処理]カンマごとでリストの格納位置を変える関数(最初のデータの持ち方が悪い場合、正しく表示できない。['小林','正一']など)
        def modify_string(value):
            # dc:creatorに含まれる余分な形式を削除するためのパターン。
            date_pattern = r'\d{4}-\d{4}|\d{4}'

            # valueをリスト型にする（リスト型のものはスキップ）
            if type(value) == str:
                value = value.split(',')
                value = [val.strip() for val in value]
                print(f'文字列をlist型に変換:{value}')

            # jsonのauthorに値が何も入っていない場合
            if not value:
                author_name = ""
                return author_name
            # jsonのauthorに値が入っている場合
            elif value:
                # print(f'Type of value: {type(value)}')
                print(value)
                author_list = []
                for num in range(len(value)):
                    # もともとstr型のデータのみdate_patternにマッチしたものの処理
                    if re.match(date_pattern, value[num]):
                        author_name = f'{value[num-2]} {value[num-1]}'
                        print(f'author_name_例外パターンにマッチした場合:{author_name}')
                        continue
                    # print(f'val:{value[num]}')
                    valList = value[num].split(',',2)
                    # print(f'valList1回目:{valList}')
                    valList = [st for st in valList if ',' not in st]
                    # print(f'valList2回目:{valList}')
                    author_name = ''.join(valList[:2])
                    # print(f'author_name:{author_name}')
                    author_list.append(author_name)
                    # print(f'author_list:{author_name}')
                    author_name = ",".join(author_list)
                    # print(f'author_name:{author_name}')
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
        i = 0
        for item in data["rss"]["channel"]["item"]:
            if i < 10:
                print(item)
                i += 1
            else:
                break

        # 図書の必要な情報をdictに格納する
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

                # 著者名をはじめからjson形式で持っていない場合の処理
                if "author" not in book_dict:
                    key = "author"
                    value = "N/A"
                    book_dict[key] = value
                    print("-------------------------------------------------------------------------")
                    print(f'キー: {key}')
                    print(f'バリュー: {value}')
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

            # book_listをsessionに保存する
            self.request.session["book_list"] = book_list
            print(str(book_list))

        # ページネーションつきのページにリダイレクトさせる
        return redirect("api:search-result")
        # except:
            # messages.info(request, "検索結果はありません。")
            # return redirect("api:top")

        # context.update({
        #     "book_list": book_list
        # })
        #
        # # 結果をテンプレートに渡して表示
        # return self.render_to_response(context)

# ページネーション処理
def paginated_view(request):
    # セッションからデータを取得
    api_data = request.session.get('book_list')

    # Paginatorの設定 (1ページに表示するアイテム数を指定)
    paginator = Paginator(api_data, 3)  # 1ページに10件表示

    # 現在のページ番号を取得
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    form = SearchForm()

    if request.method == "POST":
        print(request.POST)
        print(request.POST.get("title"))

        # お気に入りボタンを押したユーザー情報を取得
        user = request.user
        print(f'user:{user}')
        # ユーザーのインスタンスを取得
        user_instance = User.objects.get(username=user)

        # DBへの保存処理を書く↓
        title = request.POST.get("title")
        author = request.POST.get("author")
        category = request.POST.get("category")
        publisher = request.POST.get("publisher")
        thesis = request.POST.get("thesis")
        page = request.POST.get("page", "")
        publish_year = request.POST.get("publish_year")
        link = request.POST.get("link")

        # Typeモデルに登録
        if not Type.objects.filter(type=category).exists():
            # tp = Type(type=category)
            # tp.save()
            # 作成済みのtypeインスタンスが存在していなければ新規作成
            tp = Type.objects.create(
                type=category
            )
        else:
            # すでに存在していたらgetで取り出す
            tp = Type.objects.get(type=category)

        # Authorモデルに登録
        if not Author.objects.filter(author=author).exists():
            # tp = Type(type=category)
            # tp.save()
            # 作成済みのauthorインスタンスが存在していなければ新規作成
            atr = Author.objects.create(
                author=author
            )
        else:
            # すでに存在していたらgetで取り出す
            atr = Author.objects.get(author=author)
        # atr = Author(author=author)
        # atr.save()

        # Publisherモデルに登録
        if not Publisher.objects.filter(publisher=publisher).exists():
            # tp = Type(type=category)
            # tp.save()
            # 作成済みのpublisherインスタンスが存在していなければ新規作成
            pub = Publisher.objects.create(
                publisher=publisher
            )
        else:
            # すでに存在していたらgetで取り出す
            pub = Publisher.objects.get(publisher=publisher)

        # pub = Publisher(publisher=publisher)
        # pub.save()

        # Magazineモデルに登録
        if thesis:
            if not Magazine.objects.filter(magazine_title=thesis).exists():
                # tp = Type(type=category)
                # tp.save()
                # 作成済みのmagazoneインスタンスが存在していなければ新規作成
                mgz = Magazine.objects.create(
                    magazine_title=thesis
                )
            else:
                # すでに存在していたらgetで取り出す
                mgz = Magazine.objects.get(magazine_title=thesis)
            # mgz = Magazine(magazine_title=thesis)
            # mgz.save()

        print('OK')

        # Bookモデルに登録
        # publisher = Publisher.objects.get(publisher=publisher)
        if not Book.objects.filter(title=title, user=user).exists():
            book = Book.objects.create(
                title=title,
                publisher=pub,  # Publisherのインスタンスを指定
                # magazine_title=thesis,
                date=publish_year,
                page=page,
                link=link,
                user=user
            )
            print('Bookモデルに登録できました。')

            book.type.add(tp)
            book.author.add(atr)
            if thesis:
                book.magazine_title.add(mgz)

        print(Book.objects.all())

    return render(request, 'result.html', {'page_obj': page_obj, "form": form})

# プロジェクトで使用されているUserモデルの取得（Userモデルを使用するときはget_user_modelメソッドを使用する）
User = get_user_model()

# サインアップ処理（ユーザー仮登録処理）
class Signup(CreateView):
    template_name = 'signup.html'
    # model = User
    # fields = ['username', 'password'] # 必要なフィールドを指定
    form_class = UserCreateForm
    
    def form_valid(self, form):
        # フォームが有効な場合の処理
        # username = form.cleaned_data['username']
        # password = form.cleaned_data['password']

        # 仮登録と本登録用メールの発行
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('user_create/subject.txt', context)
        message = render_to_string('user_create/message.txt', context)

        user.email_user(subject, message)
        return redirect('user_create_done')

        # try:
        #     # 新しいユーザーを作成
        #     user = User.objects.create_user(username=username, password=password)
        #     print('登録の重複はありません。登録処理を実行済みです。')

        #     # 自動的にログイン
        #     login(self.request, user)

        #     # リダイレクト先を指定
        #     return redirect('api:searchafter')

        # except IntegrityError:
        #     print('登録の重複があります。登録できませんでした。')
        #     form.add_error('username', 'このユーザーはすでに登録されています')
        #     return self.form_invalid(form)

    def form_invalid(self, form):
        # フォームが無効な場合の処理
        return render(self.request, self.template_name, {'form': form})
    
# サインアップ処理（ユーザー仮登録後処理）
class UserCreateDone(TemplateView):
    template_name = 'user_create_complete'

class UserCreateComplete(TemplateView):
    # メールで受け取ったURLにアクセス後のユーザー本登録
    template_name = 'user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24) #第三引数でアクティベーションURLの期限を設定

    def get(self, request, **kwargs):
        # tokenが正しければ本登録する
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)
        # tokenが間違っていた場合の処理(アクティベーションURLが期限切れの場合を指す)
        except SignatureExpired:
            return HttpResponseBadRequest()
        # tokenがおかしい場合の処理(トークンにテキトーなものが格納されている場合を指す)
        except BadSignature:
            return HttpResponseBadRequest()
        
        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                # userの状態(is_active)がTrueでない場合
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)
        
        return HttpResponseBadRequest()


# ログイン処理
class UserLogin(LoginView):
    # template_name = 'login.html'
    # redirect_authenticated_user = True  # 既にログインしているユーザーはリダイレクト

    # def form_valid(self, form):
    #     try:
    #         # userのログインが成功する場合
    #         user = form.get_user()
    #         print('ユーザーが登録されていることを確認できました。')
    #         login(self.request, user) # ログイン処理
    #         return redirect('api:top')
        
    #     except IntegrityError:
    #         # userのログインが失敗する場合
    #         print('そのユーザーは登録されておりません。')
    #         return self.form_invalid(form)

    # def form_invalid(self, form):
    #     print('ユーザーが登録されていることを確認できませんでした')
    #     return render(self.request, self.template_name, {'form': form})

    # フォームによるログイン認証
    form_class = LoginForm
    template_name = "../templates/login.html"
    
class UserLogout(LogoutView):
    template_name = 'logout.html' #ログアウト後に表示するテンプレート

def Detailfunc(request):
    # requestの中身にpkが振られているから、それに該当するものを表示させる。
    print(request.__dict__)
    print(vars(request))
    json_str = request.body
    json_data = json.loads(json_str)
    print(json_data)
    # if request.method == 'GET':
    return redirect('detail')

# Mypageボタン処理
class BookListView(ListView, FormView):
    print("OK")
    template_name = 'mypage.html'
    context_object_name = 'book_obj'
    form_class = SearchForm
    paginate_by = 3

    def get_queryset(self):
        print('get_queryset関数OK')
        return Book.objects.filter(user=self.request.user)


