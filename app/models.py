# -*- coding: utf-8 -*-

import re

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.validators import MinValueValidator, MaxValueValidator
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from markdownx.models import MarkdownxField

from .validators import validate_legal_chars
from .constants import MINIMAL_RATING_VALUE, MAXIMAL_RATING_VALUE

"""
The different models described in this file can mostly be separated in three different parts
advisor (also known as stepper), provider and user interaction.
    The provider part includes:
        -- Scenario
        -- SubCategoryDescription
        -- Product
        -- ProductType
        -- Provider
        -- ProviderProfile
        -- Employee

    The advisor part includes:
        -- Question
        -- Answer

    The user interaction part includes:
        -- UserImage
        -- Comment

"""


def url_alias(value):
    """
    Replaces german Umlaute and white spaces in string value.

    :param value: A string that may contain german Umlaute or whitespaces
    :return: string
    """

    temp_alias = value.lower()
    temp_alias = re.sub('\W', '_', temp_alias)
    temp_alias = re.sub("ß", 'ss', temp_alias)
    temp_alias = re.sub('ä', 'a', temp_alias)
    temp_alias = re.sub('ö', 'o', temp_alias)
    temp_alias = re.sub('ü', 'u', temp_alias)

    return temp_alias


class Category(models.Model):
    """
    Describes a general category that is used to group scenarios and
    is meant as a entry point for users that want to know what can be realized using smart home appliances.
    """

    name = models.CharField(max_length=100, unique=True, validators=[validate_legal_chars])
    picture = models.ImageField(verbose_name="Bild für die Kategorie", upload_to="categories")
    backgroundPicture = models.ImageField(verbose_name="Bild für den Hintergrund", null=True, blank=True,
                                          upload_to="categories")
    short_description = models.TextField(verbose_name="Kurzbeschreibung", max_length=170, default="---")
    description = models.TextField(verbose_name="Beschreibung", default="---")
    iconString = models.CharField(max_length=20, default="gift", verbose_name="Zu verwendenes Icon")

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"
        ordering = ["name"]


class Scenario(models.Model):
    """
    Allows producers to present an idea of what can be achieved using smart home appliances.
    Unlike Categories this is supposed to be a concrete representation of projects an user can realize.
    Can be created by Employees.
    """

    name = models.CharField(max_length=255, unique=True)
    url_name = models.CharField(max_length=255, unique=False, verbose_name="URL-Name")
    description = models.TextField(verbose_name="Beschreibung", null=True, blank=True)
    picture = models.ImageField(verbose_name="Bild", null=True, blank=True, upload_to="scenarios")
    provider = models.ForeignKey("Provider", default="1", verbose_name="Erstellt von", on_delete=models.CASCADE)
    categories = models.ManyToManyField("Category", through="ScenarioCategoryRating",
                                        through_fields=('scenario', 'category'), verbose_name="Bewertung")
    meta_broker = models.ForeignKey("MetaDevice", default=None, verbose_name="Besteht aus einem Metabroker",
                                    on_delete=models.CASCADE, null=True, blank=True, related_name="broker_of_scenario")
    meta_endpoints = models.ManyToManyField(to="MetaDevice", verbose_name="Besteht aus MetaEndpointDevices",
                                            related_name="ednpoint_of_scenario")
    subcategory = models.ManyToManyField(to='SubCategory', verbose_name="Dieses Szenario ist Teil dieser Subkategorie")
    in_shopping_basket_of = models.ManyToManyField(to=Session,
                                                   verbose_name="Dieses Szenario liegt im Warenkorb von Session",
                                                   blank=True)
    thumbnail = ImageSpecField(source='picture', processors=[ResizeToFill(200, 100)], format='JPEG')
    title = models.CharField(max_length=255, default="---")

    def __str__(self):
        return '%s' % self.name

    def save(self, *args, **kwargs):
        """Saves an instance of a Scenario and sets url_name to a cleaned version of name"""
        self.url_name = url_alias(self.name)
        super(Scenario, self).save(*args, **kwargs)

        # for each rating create a rating for this element
        # first, get the categories that this scenario is not rated in
        unrated_categories = Category.objects.exclude(
                pk__in=self.categories.values_list('pk', flat=True))

        # then create a rating with the minimal value for each unrated category
        for category in unrated_categories:
            ScenarioCategoryRating(category=category, scenario=self,
                    rating=MINIMAL_RATING_VALUE).save()

    class Meta:
        verbose_name = "Szenario"
        verbose_name_plural = "Szenarien"
        ordering = ["name"]


class SubCategoryDescription(models.Model):
    """
    Part of a sub category. Enables the producer to have more control how their subcategory should look like.
    Can be created by Employees.
    """

    belongs_to_subcategory = models.ForeignKey("SubCategory", verbose_name="Beschreibung für SubKateogrie",
                                               on_delete=models.CASCADE)
    description = models.TextField(verbose_name="Beschreibung")
    image = models.ImageField(upload_to="subcategoryDesc", verbose_name="Bild")
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(200, 100)],
                               format='JPEG')
    left_right = models.BooleanField(verbose_name="Bild auf der rechten Seite zeigen")
    order = models.IntegerField(verbose_name="Reihenfolge")

    def __str__(self):
        return '%s %s' % (self.belongs_to_subcategory, self.order)

    class Meta:
        verbose_name = "SubKategoriebeschreibung"
        verbose_name_plural = "SubKategoriebeschreibungen"
        ordering = ["order"]


class Product(models.Model):
    """
    A database representation of an smart home appliance.Can be created by Employees.
    """

    name = models.CharField(max_length=200)
    provider = models.ForeignKey("Provider", default="1", on_delete=models.CASCADE, verbose_name="Produzent")
    product_type = models.ForeignKey("ProductType", default="1", verbose_name="Produktart",
                                     on_delete=models.SET_DEFAULT)
    serial_number = models.CharField(max_length=255, default="------", verbose_name="Artikelnummer")
    price = models.FloatField(verbose_name="Preis in Euro", default=0.0)
    efficiency = models.FloatField(verbose_name="Verbrauch in Watt", default=0.0)
    description = MarkdownxField(verbose_name="Beschreibung")
    image1 = models.ImageField(verbose_name="Bild 1", upload_to="products")
    image2 = models.ImageField(null=True, blank=True, verbose_name="Bild 2",
                               upload_to="products")
    image3 = models.ImageField(null=True, blank=True, verbose_name="Bild 3",
                               upload_to="products")
    thumbnail = ImageSpecField(source='image1',
                               processors=[ResizeToFill(200, 100)],
                               format='JPEG')
    end_of_life = models.BooleanField(default=False, verbose_name="EOL")
    renovation_required = models.BooleanField(default=False, verbose_name="Erfodert Renovierung")
    leader_protocol = models.ManyToManyField(to="Protocol", verbose_name="Spricht Protokoll im leader modus",
                                             related_name="protocol_leader", blank=True)
    follower_protocol = models.ManyToManyField(to="Protocol", verbose_name="Spricht Protokoll im follower modus",
                                               related_name="protocol_follower", blank=True)
    features = models.ManyToManyField(to="Feature", verbose_name="Hat Features")

    def __str__(self):
        return '%s' % self.name

    def delete(self, using=None, keep_parents=True):
        """
        Instead of deleting a product end_of_life will be set to True.
        Companies can pay to really remove a product from the database
        """

        self.end_of_life = True
        self.save()

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkte"
        ordering = ["name"]


class ProductType(models.Model):
    """
    A way to categorize and group Products.
    Could be used to implement another kind of product set,
    where you use general product types instead of specific products.
    """

    type_name = models.CharField(
            max_length=255, unique=True, verbose_name="Name")
    used_as_product_type_filter_by = models.ManyToManyField(
            to=Session, verbose_name="Als Produkttypfilter verwendet von",
            blank=True)
    svg_id = models.CharField(
            verbose_name="Id des SVG in der Hausvorschau", null=True, blank=True,
            max_length=255)
    icon = models.FileField(
            verbose_name="Bildicon", null=True, blank=True,
            upload_to="productType/house_overlay_picture")

    def __str__(self):
        return '%s' % self.type_name

    class Meta:
        verbose_name = "Produktart"
        verbose_name_plural = "Produktarten"
        ordering = ["type_name"]


class Provider(models.Model):
    """
    Every provider profile, employee and everything, an employee can create, is
    connected to this.
    """

    name = models.CharField(max_length=200, unique=False)
    is_visible = models.BooleanField(default=False, verbose_name="sichtbar")

    # Fields migrated from ProviderProfile
    public_name = models.CharField(max_length=200, unique=True, verbose_name="öffentlicher Name")
    logo_image = models.ImageField(verbose_name="Provider Logo für Szenarien und Produkte", upload_to="provider",
                                   help_text="Dieses Logo wird nur bei den Produkten als kleines Icon angezeigt.")

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Hersteller"
        verbose_name_plural = "Hersteller"
        ordering = ["name"]


class ProviderProfile(models.Model):
    """
    A relic from days long past. Originally, someone had the desire to decouple
    Providers from their public representation. Probably because it is a tiny
    bit more difficult to handle permissions for different fields (although I
    would be surprised if it is not possible at all).

    Anyway, we basically don't use this anymore. If we need fields from it, it
    is probably best to just migrate them over to Provider.
    """

    url_name = models.CharField(max_length=200, unique=True)
    profile_image = models.ImageField(verbose_name="Bild für die Profilseite", upload_to="provider", null=True,
                                      blank=True)
    banner_image = models.ImageField(verbose_name="Banner für Profilseite", upload_to="provider")
    introduction = models.TextField(verbose_name="Einleitung")
    contact_email = models.EmailField(verbose_name="Kontakt-Email")
    website = models.URLField()
    owner = models.OneToOneField(Provider, default="1", verbose_name="Eigentümer", on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.public_name

    def save(self, *args, **kwargs):
        """sets url_name to a cleaned version of name before saving"""

        self.url_name = url_alias(self.public_name)
        super(ProviderProfile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Herstellerprofil"
        verbose_name_plural = "Herstellerprofile"


class Employee(User):
    """
    Representation of an employee that has a connection to Provider identifying their employer
    """

    employer = models.ForeignKey("Provider", on_delete=models.CASCADE, verbose_name="Arbeitgeber")

    class Meta:
        verbose_name = "Angestellter"
        verbose_name_plural = "Angestellte"
        ordering = ["username"]


class UserImage(models.Model):
    """
    An image to be used in comments, every user can change it for themself
    """

    belongs_to_user = models.OneToOneField(to=User, verbose_name="gehört zu Nutzer", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="user", null=True, blank=True, verbose_name="Nutzerbild")

    def __str__(self):
        return "Bild für " + self.belongs_to_user.username

    class Meta:
        verbose_name = "Nutzerbild"
        verbose_name_plural = "Nutzbilder"
        ordering = ["belongs_to_user", ]


class Comment(models.Model):
    comment_from = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="geschrieben von")
    comment_title = models.CharField(max_length=255, verbose_name="Titel", )
    comment_content = models.TextField(verbose_name="Inhalt")
    # min value should be 0, max value should be 5, default should be 0
    rating = models.PositiveSmallIntegerField(verbose_name="Bewertung",
                                              validators=[MinValueValidator(0), MaxValueValidator(5)], default='0')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Erstellungsdatum")
    page_url = models.CharField(default='', max_length=255, verbose_name="Seiten-URL")

    def __str__(self):
        return 'Where: %s | Title: %s | By: %s' % (self.page_url, self.comment_title, self.comment_from.username)

    class Meta:
        verbose_name = "Kommentar"
        verbose_name_plural = "Kommentare"
        ordering = ["-creation_date", "comment_title", "-rating", ]


class Question(models.Model):
    MULTI_CHOICE = 'mc'
    RADIO_CHOICE = 'rc'
    DROP_CHOICE = 'dc'
    SLIDER_CHOICE = 'sc'

    ANSWER_PRESENTATION_CHOICES = (
        (MULTI_CHOICE, 'Multiple Choice'),
        (RADIO_CHOICE, 'Radiobutton'),
        (DROP_CHOICE, 'Dropdown'),
        (SLIDER_CHOICE, 'Slider')
    )
    description = models.CharField(max_length=255, null=True, blank=True,
                                   default="Diese Frage hat noch keine Beschreibung erhalten")
    icon_name = models.CharField(max_length=100, null=True, blank=True)

    question_text = models.CharField(max_length=255, null=False, blank=False, verbose_name="Fragentext")
    title = models.CharField(
            max_length=80, blank=True, verbose_name="Titel für Onboarding")
    answer_presentation = models.CharField(
        max_length=2,
        choices=ANSWER_PRESENTATION_CHOICES,
        default=MULTI_CHOICE,
        verbose_name="Anzeigenart der Anworten"
    )
    order = models.PositiveIntegerField(default=1000)

    # only for slider questions
    # TODO: add validation logic
    rating_min = models.IntegerField("Minimaler Wert für Antworten",
                                     null=True, blank=True)
    rating_max = models.IntegerField("Maximaler Wert für Antworten",
                                     null=True, blank=True)

    def __str__(self):
        return '%s -- %s' % (self.question_text, self.get_answer_presentation_display())

    class Meta:
        verbose_name = "Frage"
        verbose_name_plural = "Fragen"
        ordering = ["order", "pk"]


class Answer(models.Model):
    description = models.CharField(max_length=255, null=True, blank=True,
                                   default="Diese Antwort hat noch keine Beschreibung erhalten")
    belongs_to_question = models.ForeignKey(to="Question", on_delete=models.CASCADE, verbose_name="gehört zu Frage")
    answer_text = models.CharField(max_length=255, null=False, blank=False, verbose_name="Anworttext")
    icon_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '%s zu "%s"' % (self.answer_text, self.belongs_to_question.question_text)

    class Meta:
        verbose_name = "Antwort"
        verbose_name_plural = "Antworten"
        ordering = ['belongs_to_question_id', 'pk', ]


class Protocol(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Feature(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class MetaDevice(models.Model):
    name = models.CharField(default="---", max_length=255)
    is_broker = models.BooleanField(default=True, verbose_name="Ist das Metadevice ein Broker")
    implementation_requires = models.ManyToManyField(to="Feature",
                                                     verbose_name="Definiert von folgender Featuresammlung")

    def __str__(self):
        if self.is_broker:
            string = "Broker: "
        else:
            string = "Endpoint: "
        if len(string) > 255:
            string = string[:253] + '..'
        return string + ", ".join([i.name for i in self.implementation_requires.all()])

    def save(self, *args, **kwargs):
        super(MetaDevice, self).save(*args, **kwargs)
        self.name = self.__str__()
        super(MetaDevice, self).save(*args, **kwargs)

    class Meta:
        ordering = ['name']


class SubCategory(models.Model):
    name = models.CharField(max_length=255)
    url_name = models.CharField(max_length=100, unique=False, verbose_name="URL-Name", null=True, blank=True)
    short_description = models.TextField(verbose_name="Kurzbeschreibung", max_length="80", null=True, blank=True)
    picture = models.ImageField(verbose_name="Bild", null=True, blank=True, upload_to="subcategories")
    belongs_to_category = models.ManyToManyField(to="Category", verbose_name="Gehört zu den folgenden Kategorien")
    used_as_filter_by = models.ManyToManyField(to=Session,
                                               verbose_name="Benutzer die diese Subkategorie als Szenariofilter verwenden",
                                               blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ScenarioCategoryRating(models.Model):
    scenario = models.ForeignKey(to="Scenario", verbose_name="Szenario", related_name="category_ratings", on_delete=models.CASCADE)
    category = models.ForeignKey(to="Category", verbose_name="Kategorie", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MINIMAL_RATING_VALUE), MaxValueValidator(MAXIMAL_RATING_VALUE)],
        verbose_name="Passfaehigkeit")

    def __str__(self):
        return "%s passt zu %s mit rating %d" % (self.scenario, self.category, self.rating)

    class Meta:
        unique_together = ('scenario', 'category')
