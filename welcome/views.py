from django.views import generic
from django.shortcuts import render

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'welcome/index.html'

    def get(self,request):
        return render(request, 'welcome/index.html', {})

"""
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
        registration_status = request.GET.get('registration')
        if registration_status == 'blank_fields':
            return render(request, 'app/index_frontend.html', {'latest_category_list': Category.objects.all(),
                                                               'message': 'Bitte alle Felder ausfüllen!',
                                                               })
        if registration_status == 'success':
            return render(request, 'app/index_frontend.html', {'latest_category_list': Category.objects.all(),
                                                               'message': 'Registrierung erfolgreich!',
                                                               })
        if registration_status == 'taken':
            return render(request, 'app/index_frontend.html', {'latest_category_list': Category.objects.all(),
                                                               'message': 'Der Benutzername wird bereits verwendet!',
                                                               })
        return render(request, 'app/index_frontend.html', {'latest_category_list': Category.objects.all()})
"""
