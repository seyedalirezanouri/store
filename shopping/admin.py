from django.contrib import admin
from .models import Product, Opinion, Score, Cart, CartItem

admin.site.register(CartItem)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('product', 'number')  
    
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('track_id', 'user', 'is_purchased', 'purchased_date')
    inlines = [CartItemInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'type', 'price')
    
@admin.register(Opinion)
class Opinionadmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'is_accepted')
    def bulkAccept(self, request, queryset):
        queryset.update(is_accepted="1")
    bulkAccept.short_description = 'Accept selected opinion'
    
    def bulkReject(self, request, queryset):
        queryset.update(is_accepted="2")
    bulkReject.short_description = 'Reject selected opinion'
    
    actions = (bulkAccept ,bulkReject)

@admin.register(Score)
class Scoreadmin(admin.ModelAdmin):
    list_display = ('user','product','score')
    

