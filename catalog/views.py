from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse
from .models import Book, Author, BookInstance, Genre
from .forms import RenewBookModelForm
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
import datetime

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


# Create your views here.

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_authors = Author.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status='a').count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_authors': num_authors,
        'num_instances_available': num_instances_available,
        'num_visits': num_visits
    }
    return render(request, 'catalog/index.html', context=context)

class BookDetailView(generic.DetailView):
    model = Book

class AuthorDetailView(generic.DetailView):
    model = Author

# def booklist(request):
#     booklist = Book.objects.all()
#     context = {'booklist': booklist}

#     return render(request, 'catalog/booklist.html', context = context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 5

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksByStaffListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_staff.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    status = book_instance.status

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        book_renewal_form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if book_renewal_form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = book_renewal_form.cleaned_data['due_back']
            book_instance.status = book_renewal_form.cleaned_data['status']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        book_renewal_form = RenewBookModelForm(initial={'due_back': proposed_renewal_date, 'status': status })

    context = {
        'form': book_renewal_form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}
    permission_required = 'catalog.can_operate_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_operate_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_operate_author'

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_operate_author'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_operate_author'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_operate_author'
