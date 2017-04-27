from django.db import models
from solo.models import SingletonModel
from utils import get_file_path


class Configuration(SingletonModel):
    logo = models.FileField(upload_to=get_file_path, blank=True, null=True)
    footer_text = models.TextField()
    terms_and_services = models.TextField()
    privacy_policy = models.TextField()

    def __str__(self):
        return 'website configuration'
