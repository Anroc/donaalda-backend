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

# Beware: insert new urls minding the regex pattern matching goes top to bottom
app_name = 'app'
urlpatterns = [
    # api
    url(r'^api/v1/categoryList/$', views.CategoryList.as_view(), name='category_collection'),
    url(r'^api/v1/scenarioList/$', views.ScenarioList.as_view(), name='scenario_collection'),
    url(r'^api/v1/ScenarioDescriptionList/$', views.ScenarioDescriptionList.as_view(),
        name='ScenarioDescription_collection'),
    url(r'^api/v1/ProductSetList/$', views.ProductSetList.as_view(), name='ProductSet_collection'),
    url(r'^api/v1/ProductList/$', views.ProductList.as_view(), name='Product_collection'),
    url(r'^api/v1/ProductTypeList/$', views.ProductTypeList.as_view(), name='ProductType_collection'),
    url(r'^api/v1/ProviderList/$', views.ProviderList.as_view(), name='Provider_collection'),
    url(r'^api/v1/ProviderProfileList/$', views.ProviderProfileList.as_view(), name='ProviderProfile_collection'),
    url(r'^api/v1/EmployeeList/$', views.EmployeeList.as_view(), name='Employee_collection'),
    url(r'^api/v1/UserImageList/$', views.UserImageList.as_view(), name='UserImage_collection'),
    url(r'^api/v1/CommentList/$', views.CommentList.as_view(), name='Comment_collection'),
    url(r'^api/v1/QuestionList/$', views.QuestionList.as_view(), name='Question_collection'),
    url(r'^api/v1/AnswerList/$', views.AnswerList.as_view(), name='Answer_collection'),
    url(r'^api/v1/TagList/$', views.TagList.as_view(), name='Tag_collection'),
    url(r'^api/v1/GivenAnswersList/$', views.GivenAnswersList.as_view(), name='GivenAnswers_collection'),
    url(r'^api/v1/QuestionSetList/$', views.QuestionSetList.as_view(), name='QuestionSet_collection'),
    url(r'^api/v1/SessionTagsList/$', views.SessionTagsList.as_view(), name='SessionTags_collection'),
    url(r'^api/v1/QuestionStepList/$', views.QuestionStepList.as_view(), name='QuestionSteps_collection'),
    # specific items
    url(r'^api/v1/categoryDetail/(?P<pk>[0-9]+)/$', views.CategoryDetail.as_view(), name='category_detail_collection'),
    url(r'^api/v1/scenarioDetail/(?P<pk>[0-9]+)/$', views.ScenarioDetail.as_view(), name='scenario_detail_collection'),
    url(r'^api/v1/ScenarioDescriptionDetail/(?P<pk>[0-9]+)/$', views.ScenarioDescriptionDetail.as_view(),
        name='ScenarioDescription_detail_collection'),
    url(r'^api/v1/ProductSetDetail/(?P<pk>[0-9]+)/$', views.ProductSetDetail.as_view(), name='ProductSet_detail_collection'),
    url(r'^api/v1/ProductDetail/(?P<pk>[0-9]+)/$', views.ProductDetail.as_view(), name='Product_detail_collection'),
    url(r'^api/v1/ProductTypeDetail/(?P<pk>[0-9]+)/$', views.ProductTypeDetail.as_view(), name='ProductType_detail_collection'),
    url(r'^api/v1/ProviderDetail/(?P<pk>[0-9]+)/$', views.ProviderDetail.as_view(), name='Provider_detail_collection'),
    url(r'^api/v1/ProviderProfileDetailDetail/(?P<pk>[0-9]+)/$', views.ProviderProfileDetail.as_view(), name='ProviderProfile_detail_collection'),
    url(r'^api/v1/EmployeeDetail/(?P<pk>[0-9]+)/$', views.EmployeeDetail.as_view(), name='Employee_detail_collection'),
    url(r'^api/v1/UserImageDetail/(?P<pk>[0-9]+)/$', views.UserImageDetail.as_view(), name='UserImage_detail_collection'),
    url(r'^api/v1/CommentDetail/(?P<pk>[0-9]+)/$', views.CommentDetail.as_view(), name='Comment_detail_collection'),
    url(r'^api/v1/QuestionDetail/(?P<pk>[0-9]+)/$', views.QuestionDetail.as_view(), name='Question_detail_collection'),
    url(r'^api/v1/AnswerDetail/(?P<pk>[0-9]+)/$', views.AnswerDetail.as_view(), name='Answer_detail_collection'),
    url(r'^api/v1/TagDetail/(?P<pk>[0-9]+)/$', views.TagDetail.as_view(), name='Tag_detail_collection'),
    url(r'^api/v1/GivenAnswersDetail/(?P<pk>[0-9]+)/$', views.GivenAnswersDetail.as_view(), name='GivenAnswers_detail_collection'),
    url(r'^api/v1/QuestionSetDetail/(?P<pk>[0-9]+)/$', views.QuestionSetDetail.as_view(), name='QuestionSet_detail_collection'),
    url(r'^api/v1/SessionTagsDetail/(?P<pk>[0-9]+)/$', views.SessionTagsDetail.as_view(), name='SessionTags_detail_collection'),
    url(r'^api/v1/QuestionStepDetail/(?P<pk>[0-9]+)/$', views.QuestionStepDetail.as_view(), name='QuestionSteps_detail_collection'),
    # FIXME: login for api browser, somehow not working yet
    url(r'^api/v1/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # api end

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
