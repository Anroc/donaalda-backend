from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.adminForms import (EmployeeCreationForm,
                            EmployeeChangeForm)

# Register your models here.
from .models import (Category,
                     Scenario,
                     ProductSet,
                     Product,
                     ProductType,
                     Provider,
                     ProviderProfile,
                     Employee,
                     ScenarioDescription,
                     Comment,
                     UserImage,
                     User,
                     Question,
                     Answer,
                     Tag,
                     SessionTags,
                     QuestionSet,
                     GivenAnswers,
                     QuestionStep
                     )


class ScenarioAdmin(admin.ModelAdmin):
    actions = []

    exclude = ['url_name']

    def get_queryset(self, request):
        user = request.user
        qs = super(ScenarioAdmin, self).get_queryset(request)

        if user.is_staff and not Employee.objects.filter(pk=user.pk).exists():
            return qs

        self.exclude.extend(['provider'])
        return qs.filter(provider=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user

        if Employee.objects.filter(pk=user.pk).exists():
            obj.provider = user.employee.employer
        obj.save()


class CommentAdmin(admin.ModelAdmin):
    actions = []


class ProductSetAdmin(admin.ModelAdmin):
    actions = []

    exclude = []

    def get_queryset(self, request):
        user = request.user
        qs = super(ProductSetAdmin, self).get_queryset(request)

        if user.is_staff and not Employee.objects.filter(pk=user.pk).exists():
            return qs

        self.exclude.extend(['creator'])
        return qs.filter(creator=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user

        if Employee.objects.filter(pk=user.pk).exists():
            obj.creator = user.employee.employer

        obj.save()


class ProductAdmin(admin.ModelAdmin):
    actions = []

    exclude = []

    list_display = ('name', 'serial_number', 'provider', 'product_type', 'end_of_life')

    list_filter = ('provider', 'product_type', 'end_of_life')

    def get_queryset(self, request):
        user = request.user
        qs = super(ProductAdmin, self).get_queryset(request)
        if user.is_staff and not Employee.objects.filter(pk=user.pk).exists():
            return qs

        self.exclude.extend(['provider'])
        return qs.filter(provider=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user

        if Employee.objects.filter(pk=user.pk).exists():
            obj.provider = user.employee.employer

        obj.save()


class ProviderProfileAdmin(admin.ModelAdmin):
    actions = []

    exclude = ['url_name']

    def get_queryset(self, request):
        user = request.user
        qs = super(ProviderProfileAdmin, self).get_queryset(request)

        if user.is_staff and not Employee.objects.filter(pk=user.pk).exists():
            return qs

        self.exclude.extend(['owner'])
        return qs.filter(owner=user.employee.employer_id)

    @staticmethod
    def get_visibility(self, obj):
        return obj.owner.is_visible

    def save_model(self, request, obj, form, change):
        user = request.user

        if Employee.objects.filter(pk=user.pk).exists():
            obj.owner = user.employee.employer

        obj.save()


class UserImageInline(admin.StackedInline):
    model = UserImage


class EmployeeAdmin(UserAdmin):
    actions = []

    add_form = EmployeeCreationForm

    form = EmployeeChangeForm

    inlines = (UserImageInline,)

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

        if user.is_staff and not Employee.objects.filter(pk=user.pk).exists():
            return qs

        return qs.filter(employer=user.employee.employer_id)

    def save_model(self, request, obj, form, change):
        user = request.user

        if Employee.objects.filter(pk=user.pk).exists():
            print("Nutzer %s ist ein Angestellter:" % user.username)
            obj.employer = user.employee.employer

        obj.is_staff = True
        obj.save()


class UserAdmin(UserAdmin):
    inlines = (UserImageInline,)


class QuestionAnswerInline(admin.StackedInline):
    model = Answer


class QuestionAdmin(admin.ModelAdmin):
    inlines = (QuestionAnswerInline,)


admin.site.unregister(User)
admin.site.register(Category)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(ProductSet, ProductSetAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Provider)
admin.site.register(ProviderProfile, ProviderProfileAdmin)
admin.site.register(ProductType)
admin.site.register(ScenarioDescription)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(QuestionSet)
admin.site.register(SessionTags)
admin.site.register(GivenAnswers)
admin.site.register(QuestionStep)
