# -*- coding: utf-8 -*-

import datetime
import re
import json
import pprint

from django.contrib import messages
from django.views import generic
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from collections import ChainMap

from .models import Category, Product, Scenario, ProviderProfile, Comment, Provider, UserImage, ProductType, \
    QuestionSet, Question, Answer, Tag, ProductSet, QuestionStep, GivenAnswers
from .forms import LoginForm
from django.contrib.auth import login, logout
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import *


class IndexView(generic.DetailView):
    template_name = 'app/index.html'
    context_object_name = 'test'

    def get(self, request, *args, **kwargs):
        return render(request, 'app/index.html',
                      {'category_list': Category.objects.all(),
                       'scenarios': Scenario.objects.all(),
                       'products': Product.objects.all(),
                       'comment': Comment.objects.filter(page_url='/')[:5],
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
                                                                page_url='/provider/' + provider)[:5],
                                                            'scenario_list_from_provider': Scenario.objects.filter(
                                                                provider=(
                                                                    ProviderProfile.objects.get(
                                                                        url_name=provider).owner.pk))
                                                            })


class ContactView(generic.ListView):
    template_name = 'app/contact.html'

    # context_object_name = 'provider'

    def get(self, request, *args, **kwargs):
        # provider = kwargs.get("provider_url_name")
        return render(request, 'app/contact.html', {})


class CategoryView(generic.ListView):
    template_name = 'app/category.html'
    context_object_name = 'scenario_list_from_category'

    def get(self, request, *args, **kwargs):
        category = kwargs.get("category_name")
        print(QuestionSet.objects.exclude(category=None))
        return render(request, 'app/category.html',
                      {'scenario_list_from_category': Category.objects.get(name=category).scenario_set.all(),
                       'category_list': Category.objects.all(),
                       'category': Category.objects.get(name=category),
                       'qs_general': QuestionStep.objects.filter(name="Allgemeines"),
                       'qs_category': QuestionStep.objects.filter(name__contains="Auswahl"),
                       'qs_category_specific': QuestionStep.objects.filter(name__contains="Detail"),
                       'given_answers': GivenAnswers.objects.filter(user=request.user),
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

    # context_object_name = 'scenario'

    def get(self, request, *args, **kwargs):
        scenario = kwargs.get("current_scenario")
        return render(request, 'app/scenario.html',
                      {'current_scenario': Scenario.objects.get(url_name=scenario),
                       'comment': Comment.objects.filter(page_url='/scenarios/' + scenario)[:5],
                       })


class ProductView(generic.DetailView):
    template_name = 'app/product.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        product = kwargs.get("pk")
        return render(request, 'app/product.html',
                      {'product': Product.objects.get(pk=product),
                       'comment': Comment.objects.filter(page_url='/products/' + product)[:5],
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
# this view logs user in if existent and redirects to previous page
def login_view(request):
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
    # copy post object to delete csrf token, so json.load works
    post = request.POST.copy()
    if request.POST.get("csrfmiddlewaretoken") and request.POST.get("csrfmiddlewaretoken") is not None:
        # print(request.POST.get('csrfmiddlewaretoken'))
        del post["csrfmiddlewaretoken"]
    # dict should hold decoded JSON objects from stepper
    steps = {}
    # read from POST and interpret as JSON
    for key, value in post.items():
        steps[key] = json.loads(value)

    # "flatten" dict by recursively dismissing dicts and adding would be lost information to key
    def flatten_dict(d):
        def expand(key, value):
            if isinstance(value, dict):
                return [(str(key) + '.' + str(k), str(v)) for k, v in flatten_dict(value).items()]
            else:
                return [(key, value)]

        items = [item for k, v in d.items() for item in expand(k, v)]

        return dict(items)

    # find unnecessary JSON data, that we dont have to work with
    regex = re.compile("[0-9].(optional|completed|step|data.completed)")

    result_dic = flatten_dict(steps)

    # copy of flattened dict, to keep checking whether stuff works, can be removed on production version of function
    clean_result_dic = dict(result_dic)

    # create list of unnecessary items
    delete_list = [i for i in result_dic.keys() if regex.search(i)]

    # REGEX to find correct answer PK to substitute YES dict values
    regex_build_value = re.compile("[\d\w]*.answer[0-9]+")

    # clean clean_result_dic of non required POST data
    for item in delete_list:
        del clean_result_dic[item]

    # create list with items to be "cleaned", IE items with answer PK in key
    clean_list = [i for i in clean_result_dic.keys() if regex_build_value.search(i)]

    # replace the actual "True" answers with corresponding answer PK
    for k, v in list(clean_result_dic.items()):
        if k in clean_list:
            clean_result_dic[k] = re.sub('.*?([0-9]*)$', r'\1', k)

    """
        for k in list(clean_result_dic.keys()):
            result = re.match('.*?([0-9]+)', k)
            if result is not None:
                clean_result_dic[result.group(1)] = clean_result_dic.pop(k)

        for k, v in list(clean_result_dic.items()):
            try:
                if isinstance(int(v), int):
                    clean_result_dic[str(k)+".answer"+str(v)] = clean_result_dic.pop(k)
                    clean_result_dic[str(k) + str(v)] = 'True'
            except ValueError:
                print(v+' is not int')
    """

    given_answers = Answer.objects.filter(pk__in=list(clean_result_dic.values()))
    used_tags = [i.tag for i in given_answers]
    product_sets = ProductSet.objects.filter(tags__in=used_tags)

    # Save given_answers to database for existing users
    user = request.user
    if user.is_authenticated():
        for k, v in list(clean_result_dic.items()):
            # given_answer = GivenAnswers.objects.get(user=user)
            given_answer = GivenAnswers.objects.get(user=user)
            given_answer.user_answer.add(Answer.objects.get(pk=int(v)))

    pp = pprint.PrettyPrinter(indent=4)
    # print("\n Tags: \n")
    # print(used_tags)
    # print("\n Product_set: \n")
    # print(product_sets)
    pp.pprint(clean_result_dic)
    # print(steps)
    return render(request, 'app/result.html',
                  {'result': product_sets,
                   'tags': used_tags,
                   })


@csrf_protect
@require_http_methods(["GET", "POST"])
# this view logs user out if existent and redirects to previous page
def log_out(request):
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
    # this view registers a userprofile if username is not already taken
    # redirects and returns statusmessage
    # received formvariables: username,email,password,firstname,lastname
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
    # this view modifies attributes in a useraccount if existent
    # redirects and returns statusmessage
    # received formvariables: email, firstname,lastname,avatar(imagefile)
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
    # this view changes userpassword if useraccount is existent
    # redirects and returns statusmessage
    # received formvariables: password_old, password_new
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
    # this view deletes a user account if existent
    # redirects and returns statusmessage
    # received formvariables: password(for verification)
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
    # this view redirects you to last page saved in session and removes it from it(last page is second first page!)
    # if there are less than 2 pages in history it redirects to mainpage "/"
    redirect = "/";

    if not 'history' in request.session or not request.session[
        'history']:  # if there is no page in history redirect to mainpage(this is also the case when HTTP_REFERER is turned off)
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
    # this view gets called to update the users page history
    # current(cp) page gets accessed via HTTP_REFERER. HTTP_REFERER has to be turned on for this to work
    # formvariables: reset(is "y" if userhistory should be reset. This is the case when the user enters the mainpage "/")
    # pagehistory is saved to a list in session
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
    # this view adds a comment in the database to a certain page-url
    # received  formvariables: text, title, rating(from 0 to 5 as string), path of the page the comment is on (hidden)
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

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
