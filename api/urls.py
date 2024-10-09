from django.urls import path
from .views import SearchBook

urlpatterns = [
    path('search/', SearchBook.as_view()),
]