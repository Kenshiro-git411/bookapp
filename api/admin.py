from django.contrib import admin
from .models import Type, Author, Publisher, Magazine, Book

admin.site.register(Type)
admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(Magazine)
admin.site.register(Book)
