from django.db import models

# Create your models here.


class Category(models.Model):

    name = models.CharField(max_length=100)
    picture = models.ImageField(verbose_name="image for category", )
    description = models.TextField()
    categories = models.ManyToManyField("Scenario")

    def __str__(self):
        return '%s' % (self.name)


class Scenario(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField()
    picture = models.ImageField(verbose_name="image for scenario", )
    #provider = models.ForeignKey("Provider")


    def __str__(self):
        return '%s' % (self.name)


class ProductSet(models.Model):
    name = models.CharField(blank=True, max_length=100)
    description = models.TextField(blank=True, )
    products = models.ManyToManyField("Product")
    #provider = models.ForeignKey("Provider")

    def __str__(self):
        return ' %s: %s' % (self.id, self.name)


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image1 = models.ImageField()
    image2 = models.ImageField(null=True)
    image3 = models.ImageField(null=True)
    thumbnail = models.ImageField()
    end_of_Life = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % (self.name)
