from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from reviews.views import RegisterView
from django.urls import include
from rest_framework.routers import SimpleRouter


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    path('api/v1/auth/signup/', RegisterView.as_view(), name='register'),
    path('api/', include('api.urls'))
]
