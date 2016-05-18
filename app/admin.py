from django.contrib import admin

# Register your models here.
from app.models import *

admin.site.register(Category)
admin.site.register(Scenario)
admin.site.register(ProductSet)
admin.site.register(Product)
