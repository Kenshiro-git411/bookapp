# Generated by Django 5.1.1 on 2024-11-03 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_book_link_book_page_alter_book_magazine_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='magazine',
            name='magazine_title',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
