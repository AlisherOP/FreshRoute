from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accounts_views.home_redirect, name='home'),
    path('accounts/', include('accounts.urls')),
    path("customers/", include("customers.urls")),
    path('restaurants/', include('restaurants.urls')),
    path('delivery/', include('delivery.urls')),
    path('', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
