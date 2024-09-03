from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Review, Comment, Genre, Category, Title

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')


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


admin.site.register(User, CustomUserAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.unregister(Group)
