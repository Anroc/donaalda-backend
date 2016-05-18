from django.db import models

# Create your models here.


class Category(models.Model):

    name = models.CharField(max_length=50)
    picture = models.ImageField(verbose_name="preview image for category", )
    description = models.TextField(max_length=280)
