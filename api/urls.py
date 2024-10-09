from django.urls import path
from .views import SearchBook, SearchViewfunc

urlpatterns = [
    path('', SearchViewfunc),
    path('search/', SearchBook.as_view(), name='search'),
]