from django.urls import path
from .views import SearchBook, SearchViewfunc, Signup, UserLogin, SearchAfterViewfunc, UserLogout, Detailfunc
app_name = "api"

urlpatterns = [
    path('', SearchViewfunc, name='top'),
    path('search/', SearchBook.as_view(), name='search'),
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', UserLogin.as_view(), name='login'),
    path('searchafter/', SearchAfterViewfunc, name='searchafter' ),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('detail/', Detailfunc, name='detail'),
]