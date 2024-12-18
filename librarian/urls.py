from django.urls import path
from librarian.views import LibrarianLoginView,LibraryHistoryListAPIView

urlpatterns = [
     path('login/librarian/', LibrarianLoginView.as_view(), name='staff-login'),
     path('library-history/', LibraryHistoryListAPIView.as_view(), name='staff-login'),

]