# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-04 16:35
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0018_auto_20170427_1643'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('dimension', models.CharField(max_length=10)),
                ('category',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute_for_category',
                                   to='products.Category')),
            ],
        ),
        migrations.CreateModel(
            name='AttributeValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=80)),
                ('attribute',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute_for_value',
                                   to='products.Attribute')),
            ],
        ),
        migrations.RemoveField(
            model_name='product',
            name='attributes',
        ),
        migrations.AddField(
            model_name='attributevalue',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_for_value',
                                    to='products.Product'),
        ),
        migrations.AlterUniqueTogether(
            name='attributevalue',
            unique_together=set([('product', 'attribute')]),
        ),
    ]
