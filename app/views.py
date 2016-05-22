from django.shortcuts import render

from django.http import HttpResponse
from django.views import generic
from django.utils import timezone

from .models import Category, Scenario


# def index(request):
#    return HttpResponse("This is the startpage of our advisor")


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

