# -*- coding: utf-8 -*-

from django.contrib import messages
from django.views import generic
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Category, Product, Scenario, ProviderProfile, Comment, Provider
from .forms import LoginForm
from django.contrib.auth import login, logout
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import *


class IndexViewNew(generic.DetailView):
    template_name = 'app/indexNew.html'
    context_object_name = 'test'

    def get(self, request, *args, **kwargs):
        return render(request, 'app/indexNew.html',
                      {'latest_category_list': Category.objects.all(),
                       'scenarios': Scenario.objects.all(),
                       'products': Product.objects.all(),
                       'comment': Comment.objects.filter(page_url='/')[:5],
                       'amount_scenarios': Scenario.objects.all().count(),
                       'amount_products': Product.objects.all().count(),
                       'amount_provider': Provider.objects.all().count(),
                       })


class IndexView(generic.ListView):
    template_name = 'app/index.html'
    context_object_name = 'latest_category_list'

    def get(self, request):
        login_status = request.GET.get('login')
        if login_status == 'failed':
            return render(request, 'app/index.html', {'latest_category_list': Category.objects.all(),
                                                      'state': 'failed',
                                                      'message': 'Wrong login data!',
                                                      })
        if login_status == 'success':
            return render(request, 'app/index.html', {'latest_category_list': Category.objects.all(),
                                                      'state': 'success',
                                                      # If the user type 'app/?login=success' in the url the
                                                      # 'message' attribute will be empty. The toolbar template is
                                                      # looking for this empty String and will not show 'Welcome [NO USER]'
                                                      'message': request.user.username,
                                                      })
        registration_status = request.GET.get('registration')
        if registration_status == 'blank_fields':
            return render(request, 'app/index.html', {'latest_category_list': Category.objects.all(),
                                                      'message': 'Bitte alle Felder ausfüllen!',
                                                      })
        if registration_status == 'success':
            return render(request, 'app/index.html', {'latest_category_list': Category.objects.all(),
                                                      'message': 'Registrierung erfolgreich!',
                                                      })
        if registration_status == 'taken':
            return render(request, 'app/index.html', {'latest_category_list': Category.objects.all(),
                                                      'message': 'Der Benutzername wird bereits verwendet!',
                                                      })

        profile_status = request.GET.get('profile')
        if profile_status == 'blank_fields':
            return render(request, 'app/index.html', {'latest_category_list': Category.objects.all(),
                                                      'message': 'Zum Ändern des Passwortes altes und neues Passwort angegeben! Restliche Änderungen durchgeführt!',
                                                      })
        if profile_status == 'success':
            return render(request, 'app/index.html', {'latest_category_list': Category.objects.all(),
                                                      'message': 'Profil erfolgreich verändert!',
                                                      })
        if profile_status == 'wrong_password':
            return render(request, 'app/index.html', {'latest_category_list': Category.objects.all(),
                                                      'message': 'Passwort falsch! Das Passwort bleibt unverändert. Restliche Änderungen durchgeführt!',
                                                      })
        if profile_status == 'deleted':
            return render(request, 'app/index.html', {'latest_category_list': Category.objects.all(),
                                                      'message': 'Ihr Account wurde gelöscht!',
                                                      })

        return render(request, 'app/index.html', {'latest_category_list': Category.objects.all()})


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
    template_name = 'app/scenarioGrid.html'
    context_object_name = 'scenario_list_from_category'

    def get(self, request, *args, **kwargs):
        category = kwargs.get("category_name")
        return render(request, 'app/scenarioGrid.html',
                      {'scenario_list_from_category': Category.objects.get(name=category).scenario_set.all(),
                       'category': Category.objects.get(name=category)
                       })


class ScenariosView(generic.ListView):
    template_name = 'app/scenarioGrid.html'
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


# for frontend testing
class TestView(generic.DetailView):
    template_name = 'app/frontendTesting.html'
    context_object_name = 'test'

    def get(self, request, *args, **kwargs):
        return render(request, 'app/frontendTesting.html',
                      {})


"""
@csrf_protect
@require_http_methods(["GET","POST"])
def login_user(request):
    state = "Please log in below..."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"
                return HttpResponseRedirect('/app')
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    return render(request, 'app/loginTemplate.html', {'state': state, 'username': username})"""


@csrf_protect
@require_http_methods(["GET", "POST"])
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


"""
class LoginView(FormView):
    form_class = LoginForm
    template_name = 'app/loginTemplate.html'
    success_url = 'app/index.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.login()
        return super(LoginView, self).form_valid(form)
"""


@csrf_protect
@require_http_methods(["GET", "POST"])
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
            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            messages.success(request, 'Sie wurden erfolgreich registriert!')
            return HttpResponseRedirect(redirectpage)
        else:
            messages.error(request, 'Bitte alle Felder ausfüllen!')
            return HttpResponseRedirect(redirectpage)
    return render(request, 'app/html_templates/registrationTemplate.html', )


@csrf_protect
@require_http_methods("POST")
def profile(request):
    user = request.user
    email = request.POST.get('email')
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')

    if (request.META.get('HTTP_REFERER') is None):
        redirectpage = "/"
        print("none")
    else:
        redirectpage = request.META.get('HTTP_REFERER')

    if user is None or not User.objects.filter(username=user.username).exists():  # existiert nicht
        messages.error(request, 'Benutzer existiert nicht!')

    else:
        if firstname and not user.first_name:
            user.first_name = firstname
            messages.success(request, 'Ihr Vorname wurde erfolgreich geändert')

        elif lastname and not user.last_name == lastname:
            user.last_name = lastname
            messages.success(request, 'Ihr Nachname wurde erfolgreich geändert')

        elif email and not user.email == email:
            user.email = email
            messages.success(request, 'Ihre Email-Adresse wurde erfolgreich geändert')
        else:
            messages.info(request, "Es wurden keine Informationen geändert")

        user.save()

    return HttpResponseRedirect(redirectpage)


@csrf_protect
@require_http_methods("POST")
def change_password(request):
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
    print("back")
    if not 'history' in request.session or not request.session['history']:
        print("1")
        return HttpResponseRedirect("/")
    else:
        history = request.session['history']
        redirect = history.pop()
        if redirect == 'redirected':
            return HttpResponseRedirect("/")
        print("2")
        print(redirect)
        history.append("redirected")
        request.session['history'] = history
    print("3")
    print(history)
    print("back")
    return HttpResponseRedirect(redirect)


@csrf_protect
@require_http_methods(["GET", "POST"])
def update_pagehistory(request):
    lp = request.POST.get('lastpage')
    if not lp:
        print("no lastpage")
        return HttpResponseRedirect("/")

    if 'history' in request.session and request.session['history']:  # wenn eine history
        history = request.session['history']
        if history[-1] == "redirected":
            history.pop()
            request.session['history'] = history
            print(1)
            print(request.session['history'])
            return HttpResponseRedirect("/")
        else:
            if request.META.get('HTTP_REFERER') == lp or lp == "None":
                print(5)
                return HttpResponseRedirect("/")
            else:
                print(2)
                history.append(lp)
                request.session['history'] = history
    else:
        print(3)
        request.session['history'] = [lp]
    print(request.session['history'])
    print("update")
    print(request.POST.get('lastpage'))
    return HttpResponseRedirect("/")
