# -*- coding: utf-8 -*-

from django.contrib import messages
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
                messages.success(request, 'Sie wurden erfolgreich angemeldet.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Ihre Anmeldung ist fehlgeschlagen. Versuchen sie es erneut.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
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
    messages.success(request, 'Sie wurden erfolgreich abgemeldet!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
                messages.error(request, 'Der Benutzername ist bereits vergeben!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            messages.success(request, 'Sie wurden erfolgreich registriert!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Bitte alle Felder ausfüllen!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
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
        messages.error(request, 'Benutzer existiert nicht!')
        HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        user = User.objects.get(username=username)

    if not (passwordOld or passwordNew or passwordDelete or email or firstname or lastname):
        messages.error(request, 'Bitte alle Felder ausfüllen!')
        HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if user.check_password(passwordDelete):  # delete account
        user.delete()
        messages.success(request, 'Profil erfolgreich gelöscht!')
        HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
                messages.success(request, 'Ihr Passwort wurde erfolgreich verändert!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                messages.error(request, 'Bitte alle Felder ausfüllen!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Angegebenes Passwort falsch!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        if passwordNew:
            messages.error(request, 'Bitte alle Felder ausfüllen!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    messages.success(request, 'Ihr Profil wurde erfolgreich verändert!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_protect
@require_http_methods(["GET", "POST"])
def back(request):
    print("back")
    if not 'history' in request.session or not request.session['history']:
        print("1")
        return HttpResponseRedirect("/")
    else:
        history=request.session['history']
        redirect= history.pop()
        if redirect =='redirected':
            return HttpResponseRedirect("/")
        print("2")
        print(redirect)
        history.append("redirected")
        request.session['history']= history
    print("3")
    print(history)
    print("back")
    return HttpResponseRedirect(redirect)


@csrf_protect
@require_http_methods(["GET", "POST"])
def update_pagehistory(request):
    lp= request.POST.get('lastpage')
    if not lp:
        print("no lastpage")
        return HttpResponseRedirect("/")

    if 'history' in request.session and request.session['history']: #wenn eine history
        history = request.session['history']
        if history[-1] == "redirected" :
            history.pop()
            request.session['history'] =history
            print(1)
            print(request.session['history'])
            return HttpResponseRedirect("/")
        else:
            print(2)
            history.append(lp)
            request.session['history'] =history
    else:
        print(3)
        request.session['history'] = [lp]
    print(request.session['history'])
    print("update")
    print(request.POST.get('lastpage'))
    return HttpResponseRedirect("/")

