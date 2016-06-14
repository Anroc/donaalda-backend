"""advisor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from . import views
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings

app_name = 'app'
urlpatterns = [
    # url(r'^app/$', views.IndexView.as_view(), name='index'),
    url(r'^contact$', views.ContactView.as_view(), name='contact'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^register$', views.register_user, name='register_user'),
    url(r'^logout$', views.log_out, name='logout'),
    url(r'^scenarios/$', views.ScenariosView.as_view(), name='scenarios'),
    url(r'^scenarios/(?P<current_scenario>[\w]+)/$',
        views.ScenarioView.as_view(), name='scenario'),
    url(r'^products/(?P<pk>[0-9]+)/$', views.ProductView.as_view(), name='product'),
    url(r'^provider/(?P<provider_url_name>[\w]+)$', views.ProviderProfileView.as_view(), name='provider_profile'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^(?P<category_name>[\w]+)/$', views.CategoryView.as_view(), name='category'),
    # for frontend testing
    url(r'^app/frontendtesting$', views.TestView.as_view(), name='frontendtesting'),
    url(r'^$', views.IndexViewNew.as_view(), name='indexnew'),
]
