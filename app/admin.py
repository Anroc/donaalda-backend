from django.contrib import admin

# Register your models here.
from .models import *


class CategoryAdmin(admin.ModelAdmin):
    pass


class ProductSetAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        user = request.user
        qs = super(ProductSetAdmin, self).get_queryset(request)

        if user.is_superuser:
            return qs
        return qs.filter(creator=user.employee.employer_id)


class ScenarioAdmin(admin.ModelAdmin):
    exclude = ["provider"]

    def get_queryset(self, request):
        user = request.user
        qs = super(ScenarioAdmin, self).get_queryset(request)
        if user.is_superuser:
            print("is superuser")
            return qs
        print("%s" % user.username)
        print("%s" % user.pk)
        print("%s" % user.employee.pk)
        print("%s" % user.employee.employer_id)
        return qs.filter(provider=user.employee.employer_id)

'''
class ProductAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return get_query_set(ProductAdmin, self, request)

'''


class ProviderProfileManager(admin.ModelAdmin):

    # exclude = ["owner"]
    readonly_fields = ["owner"]

    def get_queryset(self, request):
        user = request.user
        qs = super(ProviderProfileManager, self).get_queryset(request)

        if user.is_superuser:
            return qs
        return qs.filter(owner=user.employee.employer_id)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(ProductSet, ProductSetAdmin)
admin.site.register(Product)
admin.site.register(Employee)
admin.site.register(Provider)
admin.site.register(ProviderProfile, ProviderProfileManager)
admin.site.register(ProductType)
