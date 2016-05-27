from django.db import models


# Create your models here.
# TODO: create own model for user login, short google search: best practice to not let users access admin panel

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    picture = models.ImageField(verbose_name="Bild für die Kategorie", upload_to="categories")
    description = models.TextField(verbose_name="Beschreibung")
    scenario_set = models.ManyToManyField("Scenario", verbose_name="Zur Kategorie gehörende Szenarien")

    def __str__(self):
        return '%s' % self.name

    def natural_key(self):
        return self.name

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"


class Scenario(models.Model):
    name = models.CharField(max_length=100)
    short_description = models.TextField(verbose_name="Kurzbeschreibung", max_length="255", null=True, blank=True)
    description = models.TextField(verbose_name="Beschreibung")
    picture = models.ImageField(verbose_name="Bild", null=True, blank=True)

    # provider = models.ForeignKey("Provider")

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Szenario"
        verbose_name_plural = "Szenarien"


class ProductSet(models.Model):
    name = models.CharField(blank=True, max_length=100)
    description = models.TextField(blank=True, verbose_name="Beschreibung")
    products = models.ManyToManyField("Product", verbose_name="Dazugehörige Produkte")

    # provider = models.ForeignKey("Provider")

    def __str__(self):
        return ' %s: %s' % (self.id, self.name)

    class Meta:
        verbose_name = "Produktsammlung"
        verbose_name_plural = "Produktsammlungen"


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image1 = models.ImageField()
    image2 = models.ImageField(null=True)
    image3 = models.ImageField(null=True)
    thumbnail = models.ImageField()
    end_of_Life = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.name

    def natural_key(self):
        return self.name

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkte"
