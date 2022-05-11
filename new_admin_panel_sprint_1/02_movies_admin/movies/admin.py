from django.contrib import admin
from .models import Genre, Person, Filmwork, GenreFilmwork, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    # Отображение полей в списке
    list_display = ('name', 'description',)
    ordering = ['name']
    search_fields = ['name']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    ordering = ['full_name']
    search_fields = ['full_name']


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    # tell django to use id instead of massive mount of info- raw_id_fields = ('genre',)
    # but there is a better way- autocomplete_fields = ['genre']
    # prefetch_related didn't work good
    autocomplete_fields = ['genre']


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    # tell django to use id instead of massive mount of info- raw_id_fields = ('person',)
    # another way is autocomplete_fields = ['person']
    # prefetch_related didn't work good
    autocomplete_fields = ['person']


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    # prefetch trick didn't work good- using autocomplete_fields
    # Отображение полей в списке
    list_display = ('title', 'type', 'creation_date', 'rating',)

    # Фильтрация в списке
    list_filter = ('type', 'rating')

    # Поиск по полям
    search_fields = ('title', 'description', 'id')





