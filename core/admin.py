from django.contrib import admin
from core.models import Configuration
from solo.admin import SingletonModelAdmin

admin.site.register(Configuration, SingletonModelAdmin)
