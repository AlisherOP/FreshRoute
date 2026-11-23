from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', accounts_views.RoleLoginView.as_view(), name='login'),
    path('accounts/signup/', accounts_views.signup_view, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path("customers/", include("customers.urls")),
    path('restaurants/', include('restaurants.urls')),
    path('', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
