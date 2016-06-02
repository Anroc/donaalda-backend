from django.conf import settings
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from app.adminForms import EmployeeAddForm, EmployeeChangeForm


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


class EmployeeAdmin(admin.ModelAdmin):

    form = EmployeeChangeForm

    add_form = EmployeeAddForm

    fieldsets = [
        (None, {'fields': ('username', 'password')}),
        ('persönliche Informationen', {'fields': ('first_name', 'last_name', 'email')}),
    ]

    add_fieldsets = [(None, {'fields': ('username', 'email', 'password')})]

    exclude = []

    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            self.exclude = ["employer", "is_staff", "is_superuser",
                            "user_permissions"]
            self.fieldsets.append(('Berechtigungen', {'fields': ('is_active', 'groups')}))
        else:
            self.fieldsets.append(('Berechtigungen', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                                                 'groups', 'user_permissions', 'employer')}))
        self.fieldsets.append(('Wichtige Daten', {'fields': ()}))
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(EmployeeAdmin, self).get_form(request, obj, **defaults)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(EmployeeAdmin, self).get_fieldsets(request, obj)

    def get_queryset(self, request):
        user = request.user
        qs = super(EmployeeAdmin, self).get_queryset(request)

        if user.is_superuser or user.employee.employer_id == 1:
            return qs

        return qs.filter(employer=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user

        if user.is_superuser:
            obj.save()
            return

        obj.employer = user.employee.employer
        obj.is_staff = True
        obj.save()

    @sensitive_post_parameters_m
    @csrf_protect_m
    @transaction.atomic
    def add_view(self, request, form_url='', extra_context=None):

        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:

                raise Http404()
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super(EmployeeAdmin, self).add_view(request, form_url,
                                               extra_context)


admin.site.register(Category)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(ProductSet, ProductSetAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Provider)
admin.site.register(ProviderProfile, ProviderProfileAdmin)
admin.site.register(ProductType)
