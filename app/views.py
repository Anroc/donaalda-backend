from django.views import generic


from .models import Category, Scenario
from django.views.generic.edit import FormView
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import *


class IndexView(generic.ListView):
    template_name = 'app/index_frontend.html'
    context_object_name = 'latest_category_list'

    def get_queryset(self):
        return Category.objects.all()


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


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'app/loginTemplate.tmpl.html'
    success_url = 'app/index_frontend.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.login()
        return super(LoginView, self).form_valid(form)


# TODO: create register view
