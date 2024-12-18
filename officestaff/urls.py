from django.urls import path
from officestaff.views import StaffLoginView,StudentListAPIView

urlpatterns = [
    path('login/staff/', StaffLoginView.as_view(), name='staff-login'),
    path('students/', StudentListAPIView.as_view(), name='student-list'),

]
