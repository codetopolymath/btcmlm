from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('mlm_users.urls')),  # Include mlm_users URLs under /api/
]