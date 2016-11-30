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
from . import views
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view
from django.views.generic import RedirectView

schema_view = get_swagger_view(title='Pastebin API')

router = DefaultRouter(schema_title='Pastebin API')
router.register(r'category', views.CategoryViewSet)
router.register(r'scenario', views.ScenarioViewSet)
router.register(r'scenarioDescription', views.ScenarioDescriptionViewSet)
# TODO: returns optimal(TODO: Define optimal) productSet possible constellation for a given set of scenarios in the
# TODO: shopping basket
router.register(r'product', views.ProductViewSet)
router.register(r'productType', views.ProductTypeViewSet)
router.register(r'provider', views.ProviderViewSet)
router.register(r'providerProfile', views.ProviderProfileViewSet)
router.register(r'comment', views.CommentViewSet)
# router.register(r'question', views.QuestionViewSet)
# router.register(r'answer', views.AnswerViewSet)
# router.register(r'tag', views.TagViewSet)
router.register(r'givenAnswers', views.GivenAnswersViewSet)
router.register(r'questionStep', views.QuestionStepViewSet)
# router.register(r'suggestions', views.suggestions)
# TODO: router.register(r'filter'), views.FilterStepViewSet); This will be do'ne through the SuggestedScenarioViewSet
# implements all interactions with a users shopping basket
# TODO: router.register (r'meta_device'), views.MetaDeviceViewSet)
# implements all functions required to get all meta devices of a given meta_device_type
# TODO: router.register (r'constraints', views.ConstraintsViewSet); This will be do'ne through the ProductSetViewSet Endpoint
# constraints are linked with products

# Beware: insert new urls minding the regex pattern matching goes top to bottom
app_name = 'app'
urlpatterns = [
    # api
    # url(r'^api/v1/Category/(?P<pk>[0-9]+)/highlight/$', views.CategoryHighlight.as_view()),
    url(r'^api/swagger/suggestions', views.Suggestions.as_view()),
    url(r'^api/swagger/', schema_view),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/docs/', include('rest_framework_docs.urls')),
    # FIXME: login for api/v1/ browser, somehow not working yet
    # url(r'^api/v1/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'accounts/login', RedirectView.as_view(url='/admin/login/?next=/api/swagger/')),
    url(r'accounts/logout', views.log_out),
    # api end
    # url(r'accounts/login', views.login_view),
    # url(r'^__debug__/', include(debug_toolbar.urls)),
    url(r'^impressum$', views.ImpressumView.as_view(), name='impressum'),

    url(r'^contact$', views.ContactView.as_view(), name='contact'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^register$', views.register_user, name='register_user'),
    url(r'^logout$', views.log_out, name='logout'),
    url(r'^commentreceiver$', views.commentreceiver, name='commentreceiver'),
    url(r'^back$', views.back, name='back'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^password$', views.change_password, name='password_changing'),
    url(r'^deleteaccount$', views.delete_account, name='deleteAccount'),
]
