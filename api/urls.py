from django.urls import path
from .views import SearchBook, SearchViewfunc, Signup, UserLogin, SearchAfterViewfunc, LogoutView

urlpatterns = [
    path('', SearchViewfunc, name=''),
    path('search/', SearchBook.as_view(), name='search'),
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', UserLogin.as_view(), name='login'),
    path('searchafter/', SearchAfterViewfunc, name='searchafter' ),
    path('logout/', LogoutView.as_view(), name='logout'),
]