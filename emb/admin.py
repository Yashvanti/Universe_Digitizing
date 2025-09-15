from django.contrib import admin
from .models import Customer,Product,Orders,Feedback
# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Customer, CustomerAdmin)

class ProductAdmin(admin.ModelAdmin):
    pass
admin.site.register(Product, ProductAdmin)

class OrderAdmin(admin.ModelAdmin):
    pass
admin.site.register(Orders, OrderAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    pass
admin.site.register(Feedback, FeedbackAdmin)
# Register your models here.

from django.contrib import admin
from .models import Quote

@admin.register(Quote)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'design_name', 'size', 'phone_number', 'email', 'submission_date')
    search_fields = ('full_name', 'email', 'design_name')
    list_filter = ('size', 'submission_date')

from django.contrib import admin
from .models import Portfolio

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)

admin.site.register(Portfolio, PortfolioAdmin)

from .models import File

admin.site.register(File)
