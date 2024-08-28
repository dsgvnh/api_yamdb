from django.contrib import admin

from .models import Review, Comment, Genre, Category, Title


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'pub_date', 'title', 'text', 'score')
    search_fields = ('author',)
    list_filter = ('pub_date',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'text', 'review', 'pub_date')
    search_fields = ('author',)
    list_filter = ('pub_date',)


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('slug',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('slug',)


class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'category', 'year')
    search_fields = ('name',)
    list_filter = ('year', )


admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Title, TitleAdmin)
