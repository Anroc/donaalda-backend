from django.db import models
from django.contrib.auth.models import User

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

# Create your models here.


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
    provider = models.ForeignKey("Provider", default="1", )
    scenario_product_set = models.ForeignKey("ProductSet", null=True)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Szenario"
        verbose_name_plural = "Szenarien"


class ProductSet(models.Model):
    name = models.CharField(blank=True, max_length=100)
    description = models.TextField(blank=True, verbose_name="Beschreibung")
    products = models.ManyToManyField("Product", verbose_name="Dazugehörige Produkte")
    creator = models.ForeignKey("Provider", default="1")

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        verbose_name = "Produktsammlung"
        verbose_name_plural = "Produktsammlungen"


class Product(models.Model):
    name = models.CharField(max_length=200)
    provider = models.ForeignKey("Provider", default="1")
    product_type = models.ForeignKey("ProductType", default="0")
    serial_number = models.CharField(max_length=255, default="------")
    description = models.TextField()
    image1 = models.ImageField()
    image2 = models.ImageField(null=True, blank=True)
    image3 = models.ImageField(null=True, blank=True)
    thumbnail = ImageSpecField(source='image1',
                               processors=[ResizeToFill(200, 100)],
                               format='JPEG',)
    end_of_life = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.name

    def delete(self, using=None, keep_parents=True):
        self.end_of_life = True
        self.save()

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkte"
        # unique_together = (("provider", "serial_number"),) # It seems like unique_together does not work with ForeignKey


class ProductType(models.Model):
    type_name = models.CharField(max_length=255)

    def __str__(self):
        return '%s' % self.type_name

    class Meta:
        verbose_name = "Produktart"
        verbose_name_plural = "Produktarten"


class Provider(models.Model):
    name = models.CharField(max_length=200, unique=True, )

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Hersteller"
        verbose_name_plural = "Hersteller"


class ProviderProfile(models.Model):
    public_name = models.CharField(max_length=200, unique=True,)
    logo_image = models.ImageField()
    banner_image = models.ImageField()
    introduction = models.TextField()
    contact_email = models.EmailField()
    website = models.URLField()
    owner = models.OneToOneField("Provider", default="1")

    def __str__(self):
        return '%s' % self.public_name


    class Meta:
        verbose_name = "Herstellerprofil"
        verbose_name_plural = "Herstellerprofile"


class Employee(User):
    employer = models.ForeignKey("Provider")

    class Meta:
        verbose_name = "Angestellter"
        verbose_name_plural = "Angestellte"
