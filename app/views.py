# -*- coding: utf-8 -*-

import datetime
import json
import pprint

from django.contrib import messages
from django.views import generic
from django.contrib.auth import authenticate
from .forms import LoginForm
from django.contrib.auth import login, logout
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import *
from rest_framework import viewsets
from django.core import serializers as serial
from .serializers import *
from .permissions import *
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.decorators import *
from rest_framework import generics, mixins, views, status
from collections import namedtuple
from .validators import *
from django.core.exceptions import ValidationError

from .match_making import implement_scenario
from .suggestions import SuggestionsInputSerializer, InvalidGETException


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ScenarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer


class SubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


class SubCategoryDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubCategoryDescription.objects.all()
    serializer_class = SubCategoryDescriptionSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(end_of_life=False)
    serializer_class = ProductSerializer


class ProductTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer


class ProviderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class ProviderProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProviderProfile.objects.all()
    serializer_class = ProviderSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    def create(self, request, *args, **kwargs):
        """ creates a Comment object """
        return super(CommentViewSet, self).create(request)

    def retrieve(self, request, pk=None, **kwargs):
        """Returns a single Comment item"""
        return super(CommentViewSet, self).retrieve(request, pk)

    def update(self, request, *args, **kwargs):
        """Updates a single Comment item"""
        return super(CommentViewSet, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Partial update a Comment """
        return super(CommentViewSet, self).partial_update(request, *args, **kwargs)

    def destroy(self, request, pk=None, **kwargs):
        """Delete a Comment"""
        return super(CommentViewSet, self).destroy(request, pk)


# TODO: Refactor this endpoint to work with the current design of the process
class GivenAnswersViewSet(viewsets.ModelViewSet):
    queryset = GivenAnswers.objects.all()
    serializer_class = GivenAnswersSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    def create(self, request, *args, **kwargs):
        """ creates a GivenAnswers object """
        return super(GivenAnswersViewSet, self).create(request)

    def retrieve(self, request, pk=None, **kwargs):
        """Returns a single GivenAnswers item"""
        return super(GivenAnswersViewSet, self).retrieve(request, pk)

    def update(self, request, *args, **kwargs):
        """Updates a single GivenAnswers item"""
        return super(GivenAnswersViewSet, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Partial update a GivenAnswers """
        return super(GivenAnswersViewSet, self).partial_update(request, *args, **kwargs)

    def destroy(self, request, pk=None, **kwargs):
        """Delete a GivenAnswers"""
        return super(GivenAnswersViewSet, self).destroy(request, pk)


class QuestionStepViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuestionStep.objects.all()
    serializer_class = QuestionStepSerializer


# TODO: Find correct SuperClass if it exists, else implement self
class SuggestedScenarioViewSet():
    pass


@list_route(methods=['POST'])
@permission_classes((permissions.AllowAny,))
class Suggestions(generics.ListAPIView):
    def post(self, request, format=None):
        input_serializer = SuggestionsInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        self.request.session['suggestions_input'] = input_serializer.save()
        return self.list(request)

    def get_queryset(self):
        suggestions_input = self.request.session.get('suggestions_input', None)
        if suggestions_input is None:
            raise InvalidGETException

        for scenario in Scenario.objects.all():
            product_set = implement_scenario(
                    scenario, suggestions_input.product_preference)
            if product_set:
                yield scenario

    def get_serializer_class(self):
        return ScenarioSerializer


@api_view(['GET'])
@list_route(methods=['GET'])
@permission_classes((permissions.AllowAny,))
def matching(request):
    for scenario in set(Scenario.objects.all()):
        product_set = implement_scenario(scenario, request.GET.get('preference', 'cost'))
        print(product_set)
    return Response(status=status.HTTP_200_OK)


class IndexView(generic.DetailView):
    template_name = 'app/index.html'
    context_object_name = 'test'

    def get(self, request, *args, **kwargs):
        return render(request, 'app/index.html',
                      {'category_list': Category.objects.all(),
                       'scenarios': Scenario.objects.all(),
                       'products': Product.objects.all(),
                       'comment': Comment.objects.filter(page_url='/')[:6],
                       'amount_scenarios': Scenario.objects.all().count(),
                       'amount_products': Product.objects.all().count(),
                       'amount_provider': Provider.objects.all().count(),
                       })


class ProviderProfileView(generic.ListView):
    template_name = 'app/providerProfile.html'
    context_object_name = 'provider'

    def get(self, request, *args, **kwargs):
        provider = kwargs.get("provider_url_name")
        return render(request, 'app/providerProfile.html', {'provider': ProviderProfile.objects.get(url_name=provider),
                                                            'provider_products': Product.objects.filter(
                                                                provider=ProviderProfile.objects.get(
                                                                    url_name=provider).owner.pk),
                                                            'comment': Comment.objects.filter(
                                                                page_url='/provider/' + provider)[:6],
                                                            'scenario_list_from_provider': Scenario.objects.filter(
                                                                provider=(
                                                                    ProviderProfile.objects.get(
                                                                        url_name=provider).owner.pk))
                                                            })


class ContactView(generic.ListView):
    template_name = 'app/contact.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'app/contact.html', {})


class ImpressumView(generic.ListView):
    template_name = 'app/impressum.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'app/impressum.html', {})


class CategoryView(generic.ListView):
    template_name = 'app/category.html'
    context_object_name = 'scenario_list_from_category'

    def get(self, request, *args, **kwargs):
        category = kwargs.get("category_name")
        given_answers = []
        if request.user.is_authenticated() and GivenAnswers.objects.filter(user=request.user).exists():
            given_answers = GivenAnswers.objects.get(user=request.user).user_answer.all()
        return render(request, 'app/category.html',
                      {'scenario_list_from_category': Category.objects.get(name=category).scenario_set.all(),
                       'category_list': Category.objects.all(),
                       'category': Category.objects.get(name=category),
                       'qs_general': QuestionStep.objects.filter(name="Allgemeines"),
                       'qs_category': QuestionStep.objects.filter(name__contains="Auswahl"),
                       'qs_category_specific': QuestionStep.objects.filter(name__contains="Detail").order_by(
                           'question_steps__order'),
                       'given_answers': given_answers,
                       })


class ScenariosView(generic.ListView):
    template_name = 'app/category.html'
    context_object_name = 'scenario_list_from_category'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,
                      {'scenario_list_from_category': Scenario.objects.all(),
                       })


class ScenarioView(generic.DetailView):
    template_name = 'scenario.html'

    def get(self, request, *args, **kwargs):
        scenario = kwargs.get("current_scenario")
        return render(request, 'app/scenario.html',
                      {'current_scenario': Scenario.objects.get(url_name=scenario),
                       'comment': Comment.objects.filter(page_url='/scenarios/' + scenario)[:6],
                       })


class ProductView(generic.DetailView):
    template_name = 'app/product.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        product = kwargs.get("pk")
        return render(request, 'app/product.html',
                      {'product': Product.objects.get(pk=product),
                       'comment': Comment.objects.filter(page_url='/products/' + product)[:6],
                       })


class AllProductsView(generic.DetailView):
    template_name = 'app/allProducts.html'
    context_object_name = 'all_products'

    def get(self, request, *args, **kwargs):
        return render(request, 'app/allProducts.html',
                      {'all_products': Product.objects.all(),
                       'category_list': Category.objects.all(),
                       'provider_list': Provider.objects.all(),
                       'producttype_list': ProductType.objects.all(),
                       })


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    this view logs user in if existent and redirects to previous page

    :param request: web request made by client to server containing all available information.
    :return: webpage to redirect to and message wether login was successful or not.
    """

    if (request.META.get('HTTP_REFERER') is None):
        redirectpage = "/"
        print("none")
    else:
        redirectpage = request.META.get('HTTP_REFERER')

    form = LoginForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            user = form.login(request)
            if user is not None:
                login(request, user)
                messages.success(request, 'Sie wurden erfolgreich angemeldet.')
                return HttpResponseRedirect(redirectpage)
        else:
            messages.error(request, 'Ihre Anmeldung ist fehlgeschlagen. Versuchen sie es erneut.')
            return HttpResponseRedirect(redirectpage)
    return render(request, 'app/html_templates/loginTemplate.html', {'login_form': form})


@csrf_protect
@require_http_methods(["GET", "POST"])
def stepper_check(request):
    """
    Get the answers given by a user to questions in the stepper,stores them in the database and returns the best fitting to the user.

    :param request: Web request to server containing the given answers.
    :return: Productsets matching to the users preferences
    """
    return render(request, 'app/result.html', )


@csrf_protect
@require_http_methods(["GET", "POST"])
def log_out(request):
    """this view logs user out if existent and redirects to previous page"""

    if (request.META.get('HTTP_REFERER') is None):
        redirectpage = "/"
        print("none")
    else:
        redirectpage = request.META.get('HTTP_REFERER')
    logout(request)
    messages.success(request, 'Sie wurden erfolgreich abgemeldet!')
    return HttpResponseRedirect(redirectpage)


@csrf_protect
@require_http_methods(["GET", "POST"])
def register_user(request):
    """
    this view registers a userprofile if username is not already taken.

    :param request: received formvariables: username,email,password,firstname,lastname
    :return: redirects and returns statusmessage
    """

    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')

    if (request.META.get('HTTP_REFERER') is None):
        redirectpage = "/"
        print("none")
    else:
        redirectpage = request.META.get('HTTP_REFERER')

    if request.POST:
        if username and password and email and firstname and lastname:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Der Benutzername ist bereits vergeben!')
                return HttpResponseRedirect(redirectpage)
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messages.error(request, 'Das ist keine valide Emailadresse!')
                return HttpResponseRedirect(redirectpage)
            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            messages.success(request, 'Sie wurden erfolgreich registriert!')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Sie wurden erfolgreich angemeldet!')
            return HttpResponseRedirect(redirectpage)
        else:
            messages.error(request, 'Bitte alle Felder ausfüllen!')
            return HttpResponseRedirect(redirectpage)
    return render(request, 'app/html_templates/registrationTemplate.html', )


@csrf_protect
@require_http_methods("POST")
def profile(request):
    """
    this view modifies attributes in a useraccount if existent

    :param request: received formvariables: email, firstname,lastname,avatar(imagefile)
    :return: redirects and returns statusmessage
    """

    user = request.user
    email = request.POST.get('email')
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')
    try:
        avatar_image = request.FILES['avatar']
    except:
        avatar_image = None

    if (request.META.get('HTTP_REFERER') is None):
        redirectpage = "/"
        print("none")
    else:
        redirectpage = request.META.get('HTTP_REFERER')

    if user is None or not User.objects.filter(username=user.username).exists():
        messages.error(request, 'Benutzer existiert nicht!')

    else:
        if firstname and not user.first_name == firstname:
            user.first_name = firstname
            messages.success(request, 'Ihr Vorname wurde erfolgreich geändert')

        if lastname and not user.last_name == lastname:
            user.last_name = lastname
            messages.success(request, 'Ihr Nachname wurde erfolgreich geändert')

        if email and not user.email == email:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messages.error(request, 'Das ist keine valide Emailadresse!')
                HttpResponseRedirect(redirectpage)
            else:
                user.email = email
                messages.success(request, 'Ihre Email-Adresse wurde erfolgreich geändert')

        if avatar_image:
            print(avatar_image)
            userimage = None

            if UserImage.objects.filter(belongs_to_user=user).exists():
                userimage = user.userimage
            else:
                userimage = UserImage(belongs_to_user=user)

            print("image upload")
            userimage.image = avatar_image
            userimage.save()
            messages.success(request, 'Ihr Profilbild wurde erfolgreich geändert')

        user.save()

    return HttpResponseRedirect(redirectpage)


@csrf_protect
@require_http_methods("POST")
def change_password(request):
    """
    this view changes userpassword if useraccount is existent

    :param request: received formvariables: password_old, password_new
    :return: redirects and returns statusmessage
    """

    user = request.user
    password_old = request.POST.get('password_old')
    password_new = request.POST.get('password_new')
    password_repeat = request.POST.get('password_new_repeat')

    if (request.META.get('HTTP_REFERER') is None):
        redirectpage = "/"
        print("none")
    else:
        redirectpage = request.META.get('HTTP_REFERER')

    if user is None and not User.objects.filter(username=user.username).exists():

        messages.error(request, 'Benutzer existiert nicht!')

    elif password_old is None or password_new is None or password_repeat is None:

        messages.error(request, 'Bitte alle Felder ausfüllen!')

    elif user.check_password(password_old):

        if password_new == password_repeat:

            user.set_password(password_new)
            user.save()
            messages.success(request, 'Passwort wurde erfolgreich geändert')
            logout(request)
            messages.success(request, 'Bitte melden sie sich mit ihrem neuen Passwort an')

        else:

            messages.error(request, 'Die neuen Passwörter haben nicht übereingestimmt')

    return HttpResponseRedirect(redirectpage)


@csrf_protect
@require_http_methods("POST")
def delete_account(request):
    """
    this view deletes a user account if existent

    :param request: received formvariables: password(for verification)
    :return: redirects and returns statusmessage
    """

    user = request.user
    password = request.POST.get("password")

    if (request.META.get('HTTP_REFERER') is None):
        redirectpage = "/"
        print("none")
    else:
        redirectpage = request.META.get('HTTP_REFERER')

    if user is None or not User.objects.filter(username=user.username).exists():

        messages.error(request, "Der angebene Nutzername existiert nicht.")

    elif user.check_password(password):

        if user.delete():

            messages.success(request, "Ihr Konto wurde erfolgreich gelöscht")

        else:

            messages.error(request, "Beim Löschen ihres Konto trat ein Fehler auf."
                                    "Bitte wenden Sie sich an den Betreiber.")

        logout(request)

    else:

        messages.error(request, "Falsches Passwort")

    return HttpResponseRedirect(redirectpage)


@csrf_protect
@require_http_methods(["GET", "POST"])
def back(request):
    """
    this view redirects you to last page saved in session and removes it from it(last page is second first page!)

    :param request: A http request to the server
    :return: if there are less than 2 pages in history it redirects to mainpage "/"
    """

    redirect = "/";

    if not 'history' in request.session or not request.session['history']:
        """
        if there is no page in history redirect to mainpage
        (this is also the case when HTTP_REFERER is turned off)
        """

        return HttpResponseRedirect("/")
    else:
        if len(request.session['history']) >= 2:
            history = request.session['history']
            history.pop()
            redirect = history.pop()
            request.session['history'] = history

    return HttpResponseRedirect(redirect)


@csrf_protect
@require_http_methods(["GET", "POST"])
def update_pagehistory(request):
    """
    this view gets called to update the users page history

    :param request: http request to the server
    :return: Redirect to /
    """

    """
    current(cp) page gets accessed via HTTP_REFERER. HTTP_REFERER has to be turned on for this to work
    formvariables: reset(is "y" if userhistory should be reset. This is the case when the user enters the mainpage "/")
    pagehistory is saved to a list in session
    """

    if request.POST.get('reset') == "y":  # if history should be reset replace with empty list
        if 'history' in request.session and request.session['history']:
            request.session['history'] = []
        return HttpResponse("/")

    cp = request.META.get('HTTP_REFERER')

    if 'history' in request.session and request.session['history']:  # check if there already is a history in session
        history = request.session['history']

        if history[-1] == cp:  # if last page is the same as current page(probably redirected) do nothing to the history
            return HttpResponse("/")
        else:  # otherwise add current page to history
            history.append(cp)
            request.session['history'] = history
    else:
        request.session['history'] = [cp]  # if no historylist yet create one with current page in session

    return HttpResponse("/")


@csrf_protect
@require_http_methods(["GET", "POST"])
def commentreceiver(request):
    """
    this view adds a comment in the database to a certain page-url

    :param request: received  formvariables: text, title, rating, path of the page the comment is on
    :return: Redirect to last page the user visited
    """

    title = request.POST.get('title')
    text = request.POST.get('text')
    path = request.POST.get('path')
    print(path)
    rating = request.POST.get('rating')
    user = request.user
    if title is None or not title or text is None or not text or rating is None or not rating:
        messages.error(request, 'Bitte alle Felder ausfüllen!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if path is None or not path or not rating in ["0", "1", "2", "3", "4", "5"]:
        messages.error(request, 'Ein Fehler ist aufgetreten!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if user is None or not User.objects.filter(username=user.username).exists():
        messages.error(request, 'Benutzer existiert nicht!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if (not path == "/"):
        path = path.rstrip("/")
    print(path)
    comment = Comment(comment_title=title, comment_content=text, page_url=path, comment_from=user, rating=rating,
                      creation_date=datetime.datetime.now())
    comment.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER') + '#fh5co-testimonials')
