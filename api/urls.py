from django.urls import path
from .views import SearchBook, SearchViewfunc, Signup, UserLogin, SearchAfterViewfunc, Logout

urlpatterns = [
    path('', SearchViewfunc, name=''),
    path('search/', SearchBook.as_view(), name='search'),
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', UserLogin.as_view(), name='login'),
    path('searchafter/', SearchAfterViewfunc, name='searchafter' ),
    path('logout/', Logout.as_view(), name='logout'),
]