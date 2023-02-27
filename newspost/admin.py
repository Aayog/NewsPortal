from django.contrib import admin
from .models import Category, NewsPost, FavoriteCategory, FavoriteReporters

class CategoryAdmin(admin.ModelAdmin):
    pass

class NewsPostAdmin(admin.ModelAdmin):
    list_filter = ('author', 'categories', 'created_at')
    search_fields = ('headline', 'author__name', 'created_at')


admin.site.register(Category, CategoryAdmin)
admin.site.register(NewsPost, NewsPostAdmin)
