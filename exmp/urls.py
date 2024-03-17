from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
from .admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path("tg/", csrf_exempt(views.TgParse)),
    path("vk/", csrf_exempt(views.VkParse))
]
