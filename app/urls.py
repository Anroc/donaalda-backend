# -*- coding: utf-8 -*-

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
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from django.views.generic import RedirectView

from .schema import static_swagger_view
from . import views

router = DefaultRouter(schema_title='Pastebin API')
router.register(r'category', views.CategoryViewSet)
router.register(r'scenario', views.ScenarioViewSet)
router.register(r'subCategory', views.SubCategoryViewSet)
router.register(r'subCategoryDescription', views.SubCategoryDescriptionViewSet)
router.register(r'product', views.ProductViewSet)
router.register(r'productType', views.ProductTypeViewSet)
router.register(r'provider', views.ProviderViewSet)
router.register(r'providerProfile', views.ProviderProfileViewSet)
router.register(r'comment', views.CommentViewSet)
router.register(r'questions', views.QuestionViewSet)

# Beware: insert new urls minding the regex pattern matching goes top to bottom
app_name = 'app'
urlpatterns = [
    url(r'^api/swagger/suggestions', views.Suggestions.as_view()),
    url(r'^api/swagger/final_product_list', views.FinalProductList.as_view()),
    url(r'^api/swagger/', static_swagger_view),
    url(r'^api/v1/', include(router.urls)),
    # FIXME: login for api/v1/ browser, somehow not working yet
    # url(r'^api/v1/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^__debug__/', include(debug_toolbar.urls)),
]
