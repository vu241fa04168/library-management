from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, logout
from accounts.forms import UserLoginForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Book, BorrowRecord
from .forms import BookPublishForm

# Helper function & Mixin for Role Check
def is_publisher(user):
    return user.is_authenticated and (user.groups.filter(name='Publisher').exists() or user.is_superuser)

class PublisherRequiredMixin(UserPassesTestMixin):
    login_url = 'login'
    
    def test_func(self):
        return is_publisher(self.request.user)
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # Authenticated but not a publisher: show permission error
            messages.error(self.request, "You do not have permission to access the Publisher dashboard.")
            return redirect('book_list')
        return super().handle_no_permission()

# 1. Student/Reader Dashboard (Book List)
class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_publisher'] = is_publisher(self.request.user)
        # Fetch book IDs currently borrowed and not returned by this user
        context['borrowed_book_ids'] = list(
            BorrowRecord.objects.filter(
                user=self.request.user, is_returned=False
            ).values_list('book_id', flat=True)
        )
        return context

# 2. Borrow Book View
class BorrowBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        
        # Check if the user already has this book borrowed and not returned
        already_borrowed = BorrowRecord.objects.filter(
            user=request.user, book=book, is_returned=False
        ).exists()
        
        if already_borrowed:
            messages.error(request, f"You have already borrowed '{book.title}' and haven't returned it yet.")
            return redirect('book_list')

        if book.available_copies > 0:
            book.available_copies -= 1
            book.save()
            
            # BorrowRecord automatically sets due_date to 14 days from now on save()
            BorrowRecord.objects.create(
                user=request.user,
                book=book
            )
            messages.success(request, f"Successfully borrowed '{book.title}'. It is now on your shelf.")
        else:
            messages.error(request, f"Sorry, '{book.title}' is currently out of stock.")
            
        return redirect('my_books')

# 3. My Borrowed Books View
class MyBorrowedBooksView(LoginRequiredMixin, ListView):
    model = BorrowRecord
    template_name = 'library/my_books.html'
    context_object_name = 'records'

    def get_queryset(self):
        # Sort so that active borrowings (not returned) show up first
        return BorrowRecord.objects.filter(user=self.request.user).order_by('is_returned', '-borrow_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_publisher'] = is_publisher(self.request.user)
        qs = self.get_queryset()
        context['active_records'] = qs.filter(is_returned=False)
        context['returned_records'] = qs.filter(is_returned=True)
        return context

# 4. Return Book View
class ReturnBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # Retrieve active borrow record (belongs to user and is_returned is False)
        record = get_object_or_404(BorrowRecord, pk=pk, user=request.user, is_returned=False)
        book = record.book
        
        # Update borrow record
        record.is_returned = True
        record.returned_date = timezone.now()
        record.save()
        
        # Return copy to inventory
        book.available_copies += 1
        book.save()
        
        messages.success(request, f"Successfully returned '{book.title}'. Thank you!")
        return redirect('my_books')

# 5. Publisher Dashboard
class PublisherDashboardView(LoginRequiredMixin, PublisherRequiredMixin, ListView):
    model = Book
    template_name = 'library/publisher_dashboard.html'
    context_object_name = 'books'

    def get_queryset(self):
        return Book.objects.filter(publisher=self.request.user).order_by('-id')

# 6. Publish (Add) New Book
class PublishBookView(LoginRequiredMixin, PublisherRequiredMixin, CreateView):
    model = Book
    form_class = BookPublishForm
    template_name = 'library/publish_book_form.html'
    success_url = reverse_lazy('publisher_dashboard')

    def form_valid(self, form):
        form.instance.publisher = self.request.user
        form.instance.available_copies = form.cleaned_data.get('total_copies', 1)
        messages.success(self.request, f"Successfully published '{form.instance.title}'!")
        return super().form_valid(form)


class PublisherLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if is_publisher(request.user):
                return redirect('publisher_dashboard')
            else:
                logout(request)
        
        form = UserLoginForm()
        return render(request, 'library/publisher_login.html', {'form': form})

    def post(self, request):
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if is_publisher(user):
                login(request, user)
                messages.success(request, f"Welcome back, Publisher {user.username}!")
                return redirect('publisher_dashboard')
            else:
                messages.error(request, "Access denied. This login portal is restricted to publishers only.")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            
        return render(request, 'library/publisher_login.html', {'form': form})


class UnpublishBookView(LoginRequiredMixin, PublisherRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        
        # Access control check: ensure current user is the publisher of this book (or admin)
        if book.publisher != request.user and not request.user.is_superuser:
            messages.error(request, "You do not have permission to unpublish this book.")
            return redirect('publisher_dashboard')
            
        # Check if the book is currently borrowed
        active_borrows = BorrowRecord.objects.filter(book=book, is_returned=False).exists()
        if active_borrows:
            messages.error(request, f"Cannot unpublish '{book.title}' because it is currently borrowed by one or more readers.")
        else:
            book.delete()
            messages.success(request, f"Successfully unpublished '{book.title}' from the catalog.")
            
        return redirect('publisher_dashboard')
