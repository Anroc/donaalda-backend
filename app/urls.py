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
                  url(r'^app/$', views.IndexView.as_view(), name='index'),
                  url(r'^app/login$', views.login_view, name='login'),
                  url(r'^app/register$', views.register_user, name='register_user'),
                  url(r'^app/logout$', views.log_out, name='logout'),
                  url(r'^app/(?P<category_name>[a-zA-Z0-9_-]+)/$', views.CategoryView.as_view(), name='category'),
                  url(r'^app/(?P<category_name>[a-zA-Z0-9_-]+)/(?P<current_scenario>[a-zA-Z0-9_-]+)/$',
                      views.ScenarioView.as_view(),
                      name='scenario'),
                  url(r'^app/products/(?P<product_name>[a-zA-Z0-9_-]+)$', views.ProductView.as_view(), name='product'),
                  url(r'^app/profile$', views.profile, name='profile'),
                  # for frontend testing
                  url(r'^app/frontendtesting$', views.TestView.as_view(), name='frontendtesting'),
                  url(r'^', views.IndexViewNew.as_view(), name='indexnew'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
