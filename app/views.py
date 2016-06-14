# -*- coding: utf-8 -*-

from django.views import generic
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Category, Product, Scenario, ProviderProfile
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

        profile_status = request.GET.get('profile')

        if profile_status == 'blank_fields':
            return render(request, 'app/indexNew.html',
                          {'message': 'Zum Ändern des Passwortes altes und neues Passwort eingeben!',
                           'latest_category_list': Category.objects.all(),
                           'scenarios': Scenario.objects.all(),
                           'products': Product.objects.all()})

        if profile_status == 'password_changed':
            return render(request, 'app/indexNew.html', {'message': 'Passwort erfolgreich verändert!',
                                                         'latest_category_list': Category.objects.all(),
                                                         'scenarios': Scenario.objects.all(),
                                                         'products': Product.objects.all()})
        if profile_status == 'wrong_password':
            return render(request, 'app/indexNew.html', {'message': 'Passwort falsch!',
                                                         'latest_category_list': Category.objects.all(),
                                                         'scenarios': Scenario.objects.all(),
                                                         'products': Product.objects.all()})
        login_status = request.GET.get('login')
        if login_status == 'success':
            return render(request, 'app/indexNew.html', {'message': 'Willkommen!',
                                                         'latest_category_list': Category.objects.all(),
                                                         'scenarios': Scenario.objects.all(),
                                                         'products': Product.objects.all()})

        if login_status == 'failed':
            return render(request, 'app/indexNew.html', {'message': 'Login fehlgeschlagen!',
                                                         'latest_category_list': Category.objects.all(),
                                                         'scenarios': Scenario.objects.all(),
                                                         'products': Product.objects.all()})

        register_status = request.GET.get('registration')
        if register_status == 'success':
            return render(request, 'app/indexNew.html', {'message': 'Sie wurden erfolgreich registriert!',
                                                         'latest_category_list': Category.objects.all(),
                                                         'scenarios': Scenario.objects.all(),
                                                         'products': Product.objects.all()})

        if register_status == 'taken':
            return render(request, 'app/indexNew.html', {'message': 'Benutzername bereits vergeben!',
                                                         'latest_category_list': Category.objects.all(),
                                                         'scenarios': Scenario.objects.all(),
                                                         'products': Product.objects.all()})
        if register_status == 'blank_fields':
            return render(request, 'app/indexNew.html', {'message': 'Bitte alle Felder ausfüllen!',
                                                         'latest_category_list': Category.objects.all(),
                                                         'scenarios': Scenario.objects.all(),
                                                         'products': Product.objects.all()})

        return render(request, 'app/indexNew.html',
                      {'latest_category_list': Category.objects.all(),
                       'scenarios': Scenario.objects.all(),
                       'products': Product.objects.all()})


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
                       # 'category': Category.objects.get(name=category)
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
        return render(request, 'app/scenario.html', {'current_scenario': Scenario.objects.get(url_name=scenario)})


class ProductView(generic.DetailView):
    template_name = 'app/product.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        product = kwargs.get("pk")
        return render(request, 'app/product.html',
                      {'product': Product.objects.get(pk=product)})


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
    form = LoginForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            user = form.login(request)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect("/?login=success")
        else:
            return HttpResponseRedirect("/?login=failed")
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
    logout(request)
    return HttpResponseRedirect("/")


@csrf_protect
@require_http_methods(["GET", "POST"])
def register_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')

    if request.POST:
        if username and password and email and firstname and lastname:
            if User.objects.filter(username=username).exists():
                return HttpResponseRedirect("/?registration=taken")
            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            return HttpResponseRedirect("/?registration=success")
        else:
            return HttpResponseRedirect("/?registration=blank_fields")
    return render(request, 'app/html_templates/registrationTemplate.html', )


@csrf_protect
@require_http_methods(["GET", "POST"])
def profile(request):
    username = request.POST.get('username')
    passwordOld = request.POST.get('password_old')
    passwordNew = request.POST.get('password_new')
    passwordDelete = request.POST.get('password_delete')
    email = request.POST.get('email')
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')

    if not User.objects.filter(username=username).exists():  # existiert nicht
        return HttpResponseRedirect("/")
    else:
        user = User.objects.get(username=username)

    if not (passwordOld or passwordNew or passwordDelete or email or firstname or lastname):
        return HttpResponseRedirect("/")

    if user.check_password(passwordDelete):  # delete account
        user.delete()
        return HttpResponseRedirect("/?profile=deleted")

    if firstname:
        user.first_name = firstname

    if lastname:
        user.last_name = lastname

    if email:
        user.email = email

    user.save()

    if passwordOld:
        if user.check_password(passwordOld):  # change password
            if passwordNew:
                user.set_password(passwordNew)
                user.save()
                user = authenticate(username=username, password=passwordNew)
                login(request, user)
                return HttpResponseRedirect("/?profile=password_changed")
            else:
                return HttpResponseRedirect("/?profile=blank_fields")
        else:
            return HttpResponseRedirect("/?profile=wrong_password")
    else:
        if passwordNew:
            return HttpResponseRedirect("/?profile=blank_fields")

    return HttpResponseRedirect("/?profile=success")


"""
    if request.POST:
        if username and password and email and firstname and lastname:
            if User.objects.filter(username=username).exists():
                return HttpResponseRedirect("/app/?registration=taken")
            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            return HttpResponseRedirect("/app/?registration=success")
        else:
            return HttpResponseRedirect("/app/?registration=blank_fields")
    return render(request, 'app/html_templates/registrationTemplate.html', )
"""
