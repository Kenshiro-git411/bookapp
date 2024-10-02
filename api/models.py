from django.db import models


class Type(models.Model):
    type = models.CharField(max_length=5)

class Author(models.Model):
    author = models.CharField(max_length=20)

class Publisher(models.Model):
    publisher = models.CharField(max_length=20)

class Magazine(models.Model):
    magazine_title = models.CharField(max_length=20)

class Book(models.Model):
    type = models.ManyToManyField(Type, blank=True)
    title = models.CharField(max_length=255)
    author = models.ManyToManyField(Author, blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT)
    date = models.CharField(max_length=10)
    magazine_title = models.ManyToManyField(Magazine, blank=True)
    magazine_number = models.CharField(max_length=20)
    magazine_date = models.CharField(max_length=10)
