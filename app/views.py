from django.views import generic

from django.contrib.auth.models import User

from .models import Category, Product
from .forms import LoginForm
from django.contrib.auth import login, logout
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import *


class IndexView(generic.ListView):
    template_name = 'app/index_frontend.html'
    context_object_name = 'latest_category_list'

    def get(self, request):
        login_status = request.GET.get('login')
        if login_status == 'failed':
            return render(request, 'app/index_frontend.html', {'latest_category_list': Category.objects.all(),
                                                               'state': 'failed',
                                                               'message': 'Wrong login data!',
                                                               })
        if login_status == 'success':
            return render(request, 'app/index_frontend.html', {'latest_category_list': Category.objects.all(),
                                                               'state': 'success',
                                                               # If the user type 'app/?login=success' in the url the
                                                               # 'message' attribute will be empty. The toolbar template is
                                                               # looking for this empty String and will not show 'Welcome [NO USER]'
                                                               'message': request.user.username,
                                                               })
        return render(request, 'app/index_frontend.html', {'latest_category_list': Category.objects.all()})


class ScenariosView(generic.ListView):
    template_name = 'app/scenariosTemplate.html'
    context_object_name = 'scenario_list_from_category'

    def get(self, request, *args, **kwargs):
        category = kwargs.get("category_name")
        return render(request, 'app/scenariosTemplate.html',
                      {'scenario_list_from_category': Category.objects.get(name=category).scenario_set.all(),
                       'category': category
                       })


class ScenarioView(generic.DetailView):
    # TODO: render scenarioTemplate (NOT scenario[S]Template)

    template_name = 'app/scenariosTemplate.html'
    context_object_name = 'product_set_from_scenario'

    def get(self, request, *args, **kwargs):
        return render(request, 'app/scenariosTemplate.html')


class ProductView(generic.DetailView):
    # TODO: render specific ProductTemplate for selected product

    template_name = 'app/productTemplate.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        product = kwargs.get("product_name")
        return render(request, 'app/productTemplate.html',
                      {'product': Product.objects.get(name=product)})


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
                return HttpResponseRedirect("/app/?login=success")
        else:
            return HttpResponseRedirect("/app/?login=failed")
    return render(request, 'app/templates/loginTemplate.html', {'login_form': form})


"""
class LoginView(FormView):
    form_class = LoginForm
    template_name = 'app/loginTemplate.html'
    success_url = 'app/index_frontend.html'

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
    return HttpResponseRedirect("/app/")


@csrf_protect
@require_http_methods(["GET", "POST"])
def register_user(request):
    state = ""
    username = password = email = firstname = lastname = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        # other attributes still to come
        # check if user already exists
        user = User.objects.create_user(username, email, password)
    state = "Sie sind angemeldet "

    return render(request, 'app/registrationTemplate.html', )
