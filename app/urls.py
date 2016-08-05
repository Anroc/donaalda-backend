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

router = DefaultRouter(schema_title='Pastebin API')
router.register(r'category', views.CategoryViewSet)
router.register(r'scenario', views.ScenarioViewSet)
router.register(r'scenarioDescription', views.ScenarioDescriptionViewSet)
router.register(r'productSet', views.ProductSetViewSet)
router.register(r'product', views.ProductViewSet)
router.register(r'productType', views.ProductTypeViewSet)
router.register(r'provider', views.ProviderViewSet)
router.register(r'providerProfile', views.ProviderProfileViewSet)
router.register(r'employee', views.EmployeeViewSet)
router.register(r'comment', views.CommentViewSet)
router.register(r'question', views.QuestionViewSet)
router.register(r'answer', views.AnswerViewSet)
router.register(r'tag', views.TagViewSet)
router.register(r'givenAnswers', views.GivenAnswersViewSet)
router.register(r'questionSet', views.QuestionSetViewSet)
router.register(r'sessionTags', views.SessionTagsViewSet)
router.register(r'questionStep', views.QuestionStepViewSet)

# Beware: insert new urls minding the regex pattern matching goes top to bottom
app_name = 'app'
urlpatterns = [
    # api
    # url(r'^api/v1/Category/(?P<pk>[0-9]+)/highlight/$', views.CategoryHighlight.as_view()),
    url(r'^api/v1/', include(router.urls)),
    # FIXME: login for api browser, somehow not working yet
    url(r'^api/v1/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # api end

    #url(r'^__debug__/', include(debug_toolbar.urls)),
    url(r'^impressum$', views.ImpressumView.as_view(), name='impressum'),

    url(r'^contact$', views.ContactView.as_view(), name='contact'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^register$', views.register_user, name='register_user'),
    url(r'^result/$', views.stepper_check, name='get_question_result'),
    url(r'^logout$', views.log_out, name='logout'),
    url(r'^commentreceiver$', views.commentreceiver, name='commentreceiver'),
    url(r'^scenarios/$', views.ScenariosView.as_view(), name='scenarios'),
    url(r'^back$', views.back, name='back'),
    url(r'^updatepagehistory$', views.update_pagehistory, name='update_pagehistory'),
    url(r'^scenarios/(?P<current_scenario>[\w]+)/$',
        views.ScenarioView.as_view(), name='scenario'),
    url(r'^products/(?P<pk>[0-9]+)/$', views.ProductView.as_view(), name='product'),
    url(r'^provider/(?P<provider_url_name>[\w]+)$', views.ProviderProfileView.as_view(), name='provider_profile'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^password$', views.change_password, name='password_changing'),
    url(r'^deleteaccount$', views.delete_account, name='deleteAccount'),
    url(r'^all_products/$', views.AllProductsView.as_view(), name='product_all'),
    url(r'^(?P<category_name>[\w]+)/$', views.CategoryView.as_view(), name='category'),
    url(r'^$', views.IndexView.as_view(), name='index'),
]
