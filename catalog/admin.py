from django.contrib import admin
from .models import Genre, Author, Book, BookInstance

# Register your models here.

admin.site.register(Genre)
# admin.site.register(Author)
# admin.site.register(Book)
# admin.site.register(BookInstance)

# Define the admin class

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

class BooksInline(admin.TabularInline):
    model = Book
    extra = 0

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    # exclude = ['first_name']
    inlines = [BooksInline]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    list_display_links = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]
    filter_horizontal = ('genre', )

# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance) 
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'imprint', 'id', 'status', 'due_back', 'borrower')
    list_filter = ('status', 'due_back')
    list_editable = ('status',)
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
