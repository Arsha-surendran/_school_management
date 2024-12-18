from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(Division)
admin.site.register(Student)
admin.site.register(LibraryHistory)
admin.site.register(FeesHistory)
admin.site.register(OfficeStaff)
admin.site.register(Librarian)
admin.site.register(Country_Codes)
admin.site.register(LibraryReview)


