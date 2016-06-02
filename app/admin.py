from django.conf import settings
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import admin as a


# Register your models here.
from app.models import (Category,
                        Scenario,
                        ProductSet,
                        Product,
                        ProductType,
                        Provider,
                        ProviderProfile,
                        Employee)

csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class ScenarioAdmin(admin.ModelAdmin):

    exclude = ["provider"]

    def get_queryset(self, request):
        user = request.user
        qs = super(ScenarioAdmin, self).get_queryset(request)

        if user.is_superuser:
            return qs

        return qs.filter(provider=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user

        if user.employee:
            obj.provider = user.employee.employer_id
            obj.save()

        obj.save()


class ProductSetAdmin(admin.ModelAdmin):

    exclude = ["creator"]

    def get_queryset(self, request):
        user = request.user
        qs = super(ProductSetAdmin, self).get_queryset(request)

        if user.is_superuser:
            return qs

        return qs.filter(creator=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user

        if user.employee:
            obj.creator = user.employee.employer_id
            obj.save()

        obj.save()


class ProductAdmin(admin.ModelAdmin):

    exclude = ["provider"]

    def get_queryset(self, request):
        user = request.user
        qs = super(ProductAdmin, self).get_queryset(request)
        if user.is_superuser:
            return qs
        return qs.filter(provider=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user
        if user.employee:
            obj.provider = user.employee.employer_id
            obj.save()

        obj.save()


class ProviderProfileAdmin(admin.ModelAdmin):

    exclude = ["owner"]

    def get_queryset(self, request):
        user = request.user
        qs = super(ProviderProfileAdmin, self).get_queryset(request)

        if user.is_superuser:
            return qs

        return qs.filter(owner=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user

        if user.employee:
            obj.owner = user.employee.employer_id
            obj.save()

        obj.save()


admin.site.register(Category)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(ProductSet, ProductSetAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Employee)
admin.site.register(Provider)
admin.site.register(ProviderProfile, ProviderProfileAdmin)
admin.site.register(ProductType)
