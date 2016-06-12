from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.adminForms import (EmployeeCreationForm,
                            EmployeeChangeForm)


# Register your models here.
from app.models import (Category,
                        Scenario,
                        ProductSet,
                        Product,
                        ProductType,
                        Provider,
                        ProviderProfile,
                        Employee,
                        ScenarioDescription,
                        )


class ScenarioAdmin(admin.ModelAdmin):

    exclude = ["provider", "url_name"]

    def get_queryset(self, request):
        user = request.user
        qs = super(ScenarioAdmin, self).get_queryset(request)

        if user.is_superuser:
            return qs

        return qs.filter(provider=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user

        if Employee.objects.filter(pk=user.pk).exists():
            obj.provider = user.employee.employer
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

        if Employee.objects.filter(pk=user.pk).exists():
            obj.creator = user.employee.employer

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

        if Employee.objects.filter(pk=user.pk).exists():
            obj.provider = user.employee.employer

        obj.save()


class ProviderProfileAdmin(admin.ModelAdmin):

    exclude = ["owner", "url_name"]

    def get_queryset(self, request):
        user = request.user
        qs = super(ProviderProfileAdmin, self).get_queryset(request)

        if user.is_superuser:
            return qs

        return qs.filter(owner=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user

        if Employee.objects.filter(pk=user.pk).exists():
            obj.owner = user.employee.employer

        obj.save()


class EmployeeAdmin(UserAdmin):
    add_form = EmployeeCreationForm

    form = EmployeeChangeForm

    fieldsets = (
        ((None, {'fields': ('username', 'password')})),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (('Permissions'), {'fields': ('is_active',
                                       'groups',)}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'employer'),
        }),
    )

    def get_queryset(self, request):
        user = request.user
        qs = super(EmployeeAdmin, self).get_queryset(request)

        if user.is_superuser:
            return qs

        return qs.filter(employer=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user

        if Employee.objects.filter(pk=user.pk).exists():
            print("Nutzer %s ist ein Angestellter:" % user.username)
            obj.employer = user.employee.employer

        obj.is_staff = True
        obj.save()


admin.site.register(Category)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(ProductSet, ProductSetAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Provider)
admin.site.register(ProviderProfile, ProviderProfileAdmin)
admin.site.register(ProductType)
admin.site.register(ScenarioDescription)
