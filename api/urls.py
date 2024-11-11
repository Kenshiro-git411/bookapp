from django.urls import path
from .views import SearchBook, SearchViewfunc, Signup, UserLogin, UserLogout, Detailfunc, paginated_view, BookListView
app_name = "api"

urlpatterns = [
    path('', SearchViewfunc, name='top'),
    path('search/', SearchBook.as_view(), name='search'), # ここは検索結果をsesionに保存だけしてsearch/result/へリダイレクトさせる
    path('search/result/', paginated_view, name='search-result'), # ページネーションつきのページを表示する
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('detail/', Detailfunc, name='detail'),
    path('mypage/', BookListView.as_view(), name='mypage'),
]