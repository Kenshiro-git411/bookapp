from django.db import models
from django.contrib.auth.models import User

# 図書種別テーブル
class Type(models.Model):
    type = models.CharField(max_length=5)

# 著者テーブル
class Author(models.Model):
    author = models.CharField(max_length=20)

# 出版社テーブル
class Publisher(models.Model):
    publisher = models.CharField(max_length=20)

# 雑誌テーブル
class Magazine(models.Model):
    magazine_title = models.CharField(max_length=20, blank=True)

# お気に入りテーブル
class Book(models.Model):
    type = models.ManyToManyField(Type, blank=True) #図書種別
    title = models.CharField(max_length=255) #資料タイトル
    author = models.ManyToManyField(Author, blank=True) #著者
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT) #出版社
    date = models.CharField(max_length=10) #出版年
    magazine_title = models.ManyToManyField(Magazine, blank=True) #掲載誌タイトル
    magazine_number = models.CharField(max_length=20, blank=True) #掲載誌関数
    magazine_date = models.CharField(max_length=10, blank=True) #掲載誌出版年
    page = models.CharField(max_length=20, blank=True) #論文掲載ページ数
    link = models.URLField(blank=True) #図書資料へのアクセスURL
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', null=True) #username
