# Generated by Django 5.1.5 on 2025-02-14 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0004_cart_cartitem_cart_unique_unpurchased_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='number',
            field=models.IntegerField(default=1),
        ),
    ]
