from django.urls import path
from .views import SearchBook, SearchViewfunc, Signup, UserLogin, UserLogout, Detailfunc, paginated_view, BookListView, UserCreateDone, UserCreateComplete, PasswordReset, PasswordResetDone, PasswordResetConfirm, PasswordResetComplete, UserSetting, export_file
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
    path('signup/signup_done', UserCreateDone.as_view(), name='signup_done'),
    path('signup/signup_complete/<token>/', UserCreateComplete.as_view(), name='user_create_complete'),
    path('password_reset/', PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('setting/', UserSetting.as_view(), name='setting'), #マイページの各種設定変更画面へ
    path('mypage/export/', export_file, name='export')
]