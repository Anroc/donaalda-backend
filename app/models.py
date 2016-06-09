# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    picture = models.ImageField(verbose_name="Bild für die Kategorie", upload_to="categories")
    backgroundPicture = models.ImageField(verbose_name="Bild für den Hintergrund", null=True, blank=True)
    description = models.TextField(verbose_name="Beschreibung")
    iconString = models.CharField(max_length=20, default="gift")
    scenario_set = models.ManyToManyField("Scenario", verbose_name="Zur Kategorie gehörende Szenarien")

    def __str__(self):
        return '%s' % self.name

    def natural_key(self):
        return self.name

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"


class Scenario(models.Model):
    name = models.CharField(max_length=100, unique=True)
    short_description = models.TextField(verbose_name="Kurzbeschreibung", max_length="255", null=True, blank=True)
    description = models.TextField(verbose_name="Beschreibung", null=True, blank=True)
    picture = models.ImageField(verbose_name="Bild", null=True, blank=True)
    provider = models.ForeignKey("Provider", default="1", )
    scenario_product_set = models.ForeignKey("ProductSet", null=True)

    def __str__(self):
        return '%s' % self.name

    def natural_key(self):
        return self.name

    class Meta:
        verbose_name = "Szenario"
        verbose_name_plural = "Szenarien"


class ScenarioDescription(models.Model):
    belongs_to_scenario = models.ForeignKey("Scenario")
    description = models.TextField()
    image = models.ImageField()
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(200, 100)],
                               format='JPEG', )
    left_right = models.BooleanField()
    order = models.IntegerField()

    def natural_key(self):
        return [self.belongs_to_scenario.natural_key(), self.order]

    class Meta:
        verbose_name = "Szenariobeschreibung"
        verbose_name_plural = "Szenariobeschreibungen"


class ProductSet(models.Model):
    name = models.CharField(max_length=100, default="------")
    description = models.TextField(blank=True, verbose_name="Beschreibung")
    products = models.ManyToManyField("Product", verbose_name="Dazugehörige Produkte")
    creator = models.ForeignKey("Provider", default="1")

    def __str__(self):
        return '%s' % (self.name)

    def natural_key(self):
        return [self.creator.natural_key(), self.name]

    class Meta:
        verbose_name = "Produktsammlung"
        verbose_name_plural = "Produktsammlungen"


class Product(models.Model):
    name = models.CharField(max_length=200)
    provider = models.ForeignKey("Provider", default="1")
    product_type = models.ForeignKey("ProductType", default="0")
    serial_number = models.CharField(max_length=255, default="------")
    description = models.TextField()
    image1 = models.ImageField(verbose_name="Bild 1", upload_to="products")
    image2 = models.ImageField(null=True, blank=True, verbose_name="Bild 2",
                               upload_to="products")
    image3 = models.ImageField(null=True, blank=True, verbose_name="Bild 3",
                               upload_to="products")
    thumbnail = ImageSpecField(source='image1',
                               processors=[ResizeToFill(200, 100)],
                               format='JPEG', )
    end_of_life = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.name

    def delete(self, using=None, keep_parents=True):
        self.end_of_life = True
        self.save()

    def natural_key(self):
        return [self.provider.natural_key(), self.serial_number]

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkte"
        # unique_together = (("provider", "serial_number"),) # It seems like unique_together does not work with ForeignKey


class ProductType(models.Model):
    type_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return '%s' % self.type_name

    def natural_key(self):
        return self.type_name

    class Meta:
        verbose_name = "Produktart"
        verbose_name_plural = "Produktarten"


class Provider(models.Model):
    name = models.CharField(max_length=200, unique=True, )
    is_visible = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.name

    def natural_key(self):
        return self.name

    class Meta:
        verbose_name = "Hersteller"
        verbose_name_plural = "Hersteller"


class ProviderProfile(models.Model):
    public_name = models.CharField(max_length=200, unique=True, )
    logo_image = models.ImageField(verbose_name="Provider Logo für Szenarien und Produkte", upload_to="provider" )
    profile_image = models.ImageField(verbose_name="Bild für die Profilseite", upload_to="provider", null=True)
    banner_image = models.ImageField(verbose_name="Banner für Profilseite", upload_to="provider")
    introduction = models.TextField()
    contact_email = models.EmailField()
    website = models.URLField()
    owner = models.OneToOneField(Provider, default="1")

    def __str__(self):
        return '%s' % self.public_name

    def natural_key(self):
        return self.owner.natural_key()

    class Meta:
        verbose_name = "Herstellerprofil"
        verbose_name_plural = "Herstellerprofile"


class Employee(User):
    employer = models.ForeignKey("Provider")

    class Meta:
        verbose_name = "Angestellter"
        verbose_name_plural = "Angestellte"
