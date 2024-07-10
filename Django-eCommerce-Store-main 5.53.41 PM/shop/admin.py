from django.contrib import admin
from .models import Category, Product, Variation, ReviewRating, ProductGallery
import admin_thumbnails
from .models import Upload, Comment

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price','new', 'discount', 'stock', 'created', 'updated', 'is_available']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_available', 'category', 'new']
    list_editable = ['price','discount', 'is_available', 'stock', 'new']
    readonly_fields = ['created', 'updated', ]
    inlines = [ProductGalleryInline]

# @admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ['product', 'variation_category', 'variation_value', 'is_active']
    list_filter = ['product', 'variation_category', 'is_active']
    list_editable = ['is_active']


admin.site.register(ReviewRating)


@admin.register(ProductGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_filter = ['product']


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ['requested_by', 'rating', 'caption', 'created_at']
    search_fields = ['requested_by', 'caption']
    list_filter = ['created_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['upload', 'text', 'created_at', 'created_user']
    search_fields = ['text', 'created_user']
    list_filter = ['created_at']