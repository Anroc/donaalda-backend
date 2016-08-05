# -*- coding: utf-8 -*-

import re
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.validators import MinValueValidator, MaxValueValidator
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from random import *
from .validators import validate_legal_chars

"""
The different models described in this file can mostly be separated in three different parts
advisor (also known as stepper), provider and user interaction.
    The provider part includes:
        -- Scenario
        -- ScenarioDescription
        -- ProductSet
        -- Product
        -- ProductType
        -- Provider
        -- ProviderProfile
        -- Employee

    The advisor part includes:
        -- QuestionStep
        -- QuestionSet
        -- Question
        -- Answer
        -- Tag
        -- SessionTags
        -- GivenAnswers

    The user interaction part includes:
        -- UserImage
        -- Comment

"""


def url_alias(value):
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

    def natural_key(self):
        return self.name

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
    name = models.CharField(max_length=100, unique=True)
    url_name = models.CharField(max_length=100, unique=False, default=random(), verbose_name="URL-Name")
    short_description = models.TextField(verbose_name="Kurzbeschreibung", max_length="80", null=True, blank=True)
    picture = models.ImageField(verbose_name="Bild", null=True, blank=True, upload_to="scenarios")
    provider = models.ForeignKey("Provider", default="1", verbose_name="Versorger", on_delete=models.CASCADE)
    scenario_product_set = models.ForeignKey("ProductSet", null=True, verbose_name="dazugehörige Produktsammlung",
                                             on_delete=models.SET_NULL)
    categories = models.ManyToManyField("Category", verbose_name="passende Kategorien")

    def __str__(self):
        return '%s' % self.name

    def natural_key(self):
        return self.name

    def save(self, *args, **kwargs):
        self.url_name = url_alias(self.name)
        super(Scenario, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Szenario"
        verbose_name_plural = "Szenarien"
        ordering = ["name"]


class ScenarioDescription(models.Model):
    """
    Part of a scenario. Enables the producer to have more control how their scenario should look like.
    Can be created by Employees.
    """
    belongs_to_scenario = models.ForeignKey("Scenario", verbose_name="Beschreibung für Szenario",
                                            on_delete=models.CASCADE)
    description = models.TextField(verbose_name="Beschreibung")
    image = models.ImageField(upload_to="scenarioDesc", verbose_name="Bild")
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(200, 100)],
                               format='JPEG')
    left_right = models.BooleanField(verbose_name="Bild auf der rechten Seite zeigen")
    order = models.IntegerField(verbose_name="Reihenfolge")

    def __str__(self):
        return '%s %s' % (self.belongs_to_scenario, self.order)

    def natural_key(self):
        return [self.belongs_to_scenario.natural_key(), self.order]

    class Meta:
        verbose_name = "Szenariobeschreibung"
        verbose_name_plural = "Szenariobeschreibungen"
        ordering = ["order"]


class ProductSet(models.Model):
    """
    A set of products that can be used to realize and is connected to specific scenarios or
    just as a representation of things that are sold together. Can be created by Employees.
    """
    name = models.CharField(max_length=100, default="------")
    description = models.TextField(blank=True, verbose_name="Beschreibung",
                                   help_text="Wenn dieses Produktset zu einem Szenario gehört,"
                                             "dann geben Sie das bitte hier mit an")
    products = models.ManyToManyField("Product", verbose_name="Dazugehörige Produkte")
    creator = models.ForeignKey("Provider", default="1", verbose_name="Ersteller", on_delete=models.CASCADE)
    tags = models.ManyToManyField(to="Tag", verbose_name="Schlagwörter")

    def __str__(self):
        return '%s' % self.name

    def natural_key(self):
        return [self.creator.natural_key(), self.name]

    class Meta:
        verbose_name = "Produktsammlung"
        verbose_name_plural = "Produktsammlungen"
        ordering = ["name"]


class Product(models.Model):
    """
    A database representation of an smart home appliance.Can be created by Employees.
    """
    name = models.CharField(max_length=200)
    provider = models.ForeignKey("Provider", default="1", on_delete=models.CASCADE, verbose_name="Produzent")
    product_type = models.ForeignKey("ProductType", default="1", verbose_name="Produktart",
                                     on_delete=models.SET_DEFAULT)
    serial_number = models.CharField(max_length=255, default="------", verbose_name="Artikelnummer")
    description = models.TextField(verbose_name="Berschreibung")
    specifications = models.TextField(default="---", verbose_name="Technische Details")
    image1 = models.ImageField(verbose_name="Bild 1", upload_to="products")
    image2 = models.ImageField(null=True, blank=True, verbose_name="Bild 2",
                               upload_to="products")
    image3 = models.ImageField(null=True, blank=True, verbose_name="Bild 3",
                               upload_to="products")
    thumbnail = ImageSpecField(source='image1',
                               processors=[ResizeToFill(200, 100)],
                               format='JPEG')
    end_of_life = models.BooleanField(default=False, verbose_name="EOL")
    tags = models.ManyToManyField(to="Tag", verbose_name="Schlagwörter")

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
        ordering = ["name"]
        # unique_together = (("provider", "serial_number"),)
        # It seems like unique_together does not work with ForeignKey


class ProductType(models.Model):
    """
    A way to categorize and group Products.
    Could be used to implement another kind of product set,
    where you use general product types instead of specific products.
    """
    type_name = models.CharField(max_length=255, unique=True, verbose_name="Name")

    def __str__(self):
        return '%s' % self.type_name

    def natural_key(self):
        return self.type_name

    class Meta:
        verbose_name = "Produktart"
        verbose_name_plural = "Produktarten"
        ordering = ["type_name"]


class Provider(models.Model):
    """
    Used to decouple provider and their public representation (ProviderProfile). Every provider profile, employee and
    everything, an employee can create, is connected to this.
    """
    name = models.CharField(max_length=200, unique=False, default=random())
    is_visible = models.BooleanField(default=False, verbose_name="sichtbar")

    def __str__(self):
        return '%s' % self.name

    def natural_key(self):
        return self.name

    class Meta:
        verbose_name = "Hersteller"
        verbose_name_plural = "Hersteller"
        ordering = ["name"]


class ProviderProfile(models.Model):
    """
    The public representation of a provider on this website.
    Contains information of the provider and also lists all products, product sets and scenarios
    that are connected to the provider.
    """
    public_name = models.CharField(max_length=200, unique=True, verbose_name="öffentlicher Name")
    url_name = models.CharField(max_length=200, unique=True, default=random())
    logo_image = models.ImageField(verbose_name="Provider Logo für Szenarien und Produkte", upload_to="provider",
                                   help_text="Dieses Logo wird nur bei den Produkten als kleines Icon angezeigt.")
    profile_image = models.ImageField(verbose_name="Bild für die Profilseite", upload_to="provider", null=True)
    banner_image = models.ImageField(verbose_name="Banner für Profilseite", upload_to="provider")
    introduction = models.TextField(verbose_name="Einleitung")
    contact_email = models.EmailField(verbose_name="Kontakt-Email")
    website = models.URLField()
    owner = models.OneToOneField(Provider, default="1", verbose_name="Eigentümer", on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.public_name

    def natural_key(self):
        return self.owner.natural_key()

    def save(self, *args, **kwargs):
        self.url_name = url_alias(self.public_name)
        super(ProviderProfile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Herstellerprofil"
        verbose_name_plural = "Herstellerprofile"
        ordering = ["public_name"]


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

    def natural_key(self):
        self.belongs_to_user.natural_key()

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


# DONE:Add reference field to tell frontend which step each question belongs to
#       -- Realized using the QuestionStep model
# DONE:Maybe which category each question belongs to? manytomany to category?
#       -- See QuestionSet
class Question(models.Model):
    MULTI_CHOICE = 'mc'
    RADIO_CHOICE = 'rc'
    DROP_CHOICE = 'dc'

    ANSWER_PRESENTATION_CHOICES = (
        (MULTI_CHOICE, 'Multiple Choice'),
        (RADIO_CHOICE, 'Radiobutton'),
        (DROP_CHOICE, 'Dropdown'),
    )

    question_text = models.CharField(max_length=255, null=False, blank=False, verbose_name="Fragentext")
    answer_presentation = models.CharField(
        max_length=2,
        choices=ANSWER_PRESENTATION_CHOICES,
        default=MULTI_CHOICE,
        verbose_name="Anzeigenart der Anworten"
    )
    order = models.PositiveIntegerField(default=1000)

    def __str__(self):
        return '%s -- %s' % (self.question_text, self.get_answer_presentation_display())

    class Meta:
        verbose_name = "Frage"
        verbose_name_plural = "Fragen"
        ordering = ["order", "pk"]


class Answer(models.Model):
    """
    Connects Tags with questions and enables tags to be used for multiple answers, but only one tag per answer.
    """
    belongs_to_question = models.ForeignKey(to="Question", on_delete=models.CASCADE, verbose_name="gehört zu Frage")
    answer_text = models.CharField(max_length=255, null=False, blank=False, verbose_name="Anworttext")
    tag = models.ForeignKey(to="Tag", on_delete=models.CASCADE, verbose_name="Schlagwort")

    def __str__(self):
        return '%s zu "%s"' % (self.answer_text, self.belongs_to_question.question_text)

    class Meta:
        verbose_name = "Antwort"
        verbose_name_plural = "Antworten"
        ordering = ['belongs_to_question_id', 'pk', ]


class Tag(models.Model):
    """
    A possibility for producers to add information to products and product sets,
    that make them easier to match with the advisor.
    Currently only product sets are used with the advisor.
    """
    code = models.CharField(max_length=45)
    name = models.CharField(max_length=255)

    def __str__(self):
        return '%s (%s)' % (self.name, self.code)

    class Meta:
        verbose_name = "Schlagwort"
        verbose_name_plural = "Schlagwörter"
        ordering = ['code', ]


class GivenAnswers(models.Model):
    """
    Used to pre-check answers a user has given the last time he was logged in and used the advisor.
    This is independent of any session id that could expire
    or something else that might have happend to the users computer.

    It does not store a history the user could use to reuse old requests.
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name="User")
    user_answer = models.ManyToManyField(to="Answer", verbose_name="hat geantwortet")

    def __str__(self):
        return '%s hat geantwortet: %s' % (self.user, str(list(self.user_answer.all())))

    class Meta:
        verbose_name = "beantwortete Antwort"
        verbose_name_plural = "beantwortete Antworten"
        # ordering = ['user', ]


class QuestionSet(models.Model):
    """
    A number of questions that have a contextual relationship and shall be grouped together.
    Also enables an order between different sets, which Question should be shown at the top and which at the lower end.
    """
    name = models.CharField(max_length=255, default="---")
    question = models.ManyToManyField("Question", verbose_name="Dazugehörige Fragen")
    category = models.OneToOneField("Category", on_delete=models.CASCADE, null=True, blank=True,
                                    verbose_name="Dazugehörige Kategorie")
    order = models.PositiveIntegerField(default=1000)

    def __str__(self):
        return '%s' % self.name

    def natural_key(self):
        return [self.name]

    class Meta:
        verbose_name = "Fragensammlung"
        verbose_name_plural = "Fragensammlungen"
        ordering = ["order", "pk"]


class SessionTags(models.Model):
    """
    Stores tags associated with the use of the advisor.
    Could be used for debugging purposes but is included for analytical and 'big data' reasons.
    (This part is not implemented as it wasn't part of the assignment)
    """
    session = models.OneToOneField(Session, null=True, on_delete=models.SET_NULL, verbose_name="Zugehörige Session")
    tag = models.ManyToManyField("Tag", verbose_name="Referenziert auf Tag")

    def __str__(self):
        return '%s %s' % (self.session_id, str(list(self.tag.all())))

    class Meta:
        verbose_name = 'Session Tag'
        verbose_name_plural = 'Session Tags'


class QuestionStep(models.Model):
    name = models.CharField(max_length=255)
    question_steps = models.ManyToManyField('QuestionSet', verbose_name="zusammen gehörende Fragen")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Fragen für Stepper-Schritt"
        verbose_name_plural = "Fragen für Stepper-Schritte"
