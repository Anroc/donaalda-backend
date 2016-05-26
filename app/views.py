from django.views import generic


from .models import Category, Scenario
from django.views.generic.edit import FormView
from .forms import LoginForm
from django.contrib.auth import authenticate, login, user_login_failed, logout
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import *
from django.core.urlresolvers import reverse, reverse_lazy


class ScenarioView(generic.ListView):
    template_name = 'app/scenarioTemplate.html'
    context_object_name = 'scenarios_from_category_list'

    def get_queryset(self, request):
        self.request.GET.get('')
        return Scenario.objects.all()


class IndexView(generic.ListView):
    template_name = 'app/index_frontend.html'
    context_object_name = 'latest_category_list'

    def get_queryset(self):
        return Category.objects.all()

    def get(self, request):
        login_status = request.GET.get('login')
        if login_status == 'failed':
            print('Login failed')
            return render(request, 'app/index_frontend.html', {'latest_category_list': Category.objects.all(),
                                                               'state': 'Login gibts heute nicht, bist du Dumm oder was?'})
        if login_status == 'success':
            print('Login successful')
            return render(request, 'app/index_frontend.html', {'latest_category_list': Category.objects.all(),
                                                               'state': 'Welcome %s' %request.user.username})
        return render(request, 'app/index_frontend.html', {'latest_category_list':Category.objects.all()})




class DetailView(generic.DetailView):
    model = Scenario
    template_name = 'app/detail.html'

    def get_queryset(self):
        return Scenario.objects.all()

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

    return render(request, 'app/loginTemplate.tmpl.html', {'state': state, 'username': username})

@csrf_protect
@require_http_methods(["GET","POST"])
def login_view(request):
    form = LoginForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            user = form.login(request)
            if user is not None:
                login(request, user)
                print("Login successful")
                return HttpResponseRedirect("/app/?login=success")
        else:
            # print("login fehlgeschlagen")
            return HttpResponseRedirect("/app/?login=failed")
    return render(request,'app/loginTemplate.tmpl.html', {'login_form': form})


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'app/loginTemplate.tmpl.html'
    success_url = 'app/index_frontend.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.login()
        return super(LoginView, self).form_valid(form)

# TODO: enable logout

@csrf_protect
@require_http_methods(["GET","POST"])
def log_out(request):
    logout(request)
    return HttpResponseRedirect("/app/")

# TODO: create register view
