from django.db import models

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
    magazine_title = models.CharField(max_length=20)

# お気に入りテーブル
class Book(models.Model):
    type = models.ManyToManyField(Type, blank=True)
    title = models.CharField(max_length=255)
    author = models.ManyToManyField(Author, blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT)
    date = models.CharField(max_length=10)
    magazine_title = models.ManyToManyField(Magazine, blank=True)
    magazine_number = models.CharField(max_length=20, blank=True)
    magazine_date = models.CharField(max_length=10, blank=True)
    page = models.CharField(max_length=20, blank=True)
    link = models.URLField(blank=True)
