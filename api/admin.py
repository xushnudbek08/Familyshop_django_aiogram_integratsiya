from django.contrib import admin
from .models import Category, Product, ProductImage, TelegramUser
# Register your models here.
from django.contrib import admin
from .models import Category, Product, ProductImage,Feedback


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Qo‘shimcha rasm qo‘shish uchun bo‘sh joy
    fields = ('image',)  # Qaysi fieldlar chiqishini belgilaymiz


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'total_price')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]  # Product ichida rasm qo‘shish
    fieldsets = (
        ('Asosiy ma’lumotlar', {
            'fields': ('category', 'name', 'description', 'size', 'color')
        }),
        ('Narxlar', {
            'fields': ('prepayment_price', 'remaining_price')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image')



from django.contrib import admin
from django.utils.html import format_html
from .models import TelegramUser, Order

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "telegram_id", "username", "phone", "created_at")
    search_fields = ("full_name", "telegram_id", "username", "phone")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_price",
        "status",
        "maps_link",
        "payment_image_preview",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__full_name", "user__telegram_id", "phone_number")
    readonly_fields = ("maps_link", "payment_image_preview", "created_at")
    fields = (
        "user",
        "product_list",
        "total_price",
        "prepayment_amount",
        "remaining_amount",
        "latitude",
        "longitude",
        "maps_link",
        "phone_number",
        "payment_screenshot",
        "payment_image_preview",
        "admin_reply",  # feedback maydoni
        "status",
        "created_at",
    )

    def maps_link(self, obj):
        if obj.latitude and obj.longitude:
            return format_html(
                '<a href="https://maps.google.com/?q={},{}" target="_blank">📍 Ko‘rish</a>',
                obj.latitude, obj.longitude
            )
        return "Lokatsiya yo‘q"

    maps_link.short_description = "Google Maps"

    def payment_image_preview(self, obj):
        if obj.payment_screenshot:
            return format_html(
                '<img src="{}" width="150" style="border:1px solid #ccc;"/>',
                obj.payment_screenshot.url
            )
        return "Yuklanmagan"

    payment_image_preview.short_description = "To‘lov rasmi"

from django.contrib import admin
from .models import Order, Feedback
from django.utils.html import format_html

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id_display', 'order_user', 'message', 'created_at')
    search_fields = ('order__user__full_name', 'message')

    def order_id_display(self, obj):
        return f"#{obj.order.id}"
    order_id_display.short_description = "Order ID"

    def order_user(self, obj):
        return obj.order.user.full_name
    order_user.short_description = "User"
