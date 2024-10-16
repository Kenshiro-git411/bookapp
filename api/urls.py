from django.urls import path
from .views import SearchBook, SearchViewfunc, Signup, Login

urlpatterns = [
    path('', SearchViewfunc),
    path('search/', SearchBook.as_view(), name='search'),
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
]