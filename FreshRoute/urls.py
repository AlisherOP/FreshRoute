from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts import views as accounts_views
from FreshRoute import views as core_views

# Custom Admin Site Branding
admin.site.site_header = "FreshRoute Operations HQ"
admin.site.site_title = "FreshRoute Admin Portal"
admin.site.index_title = "Platform Operations & Management"

urlpatterns = [
    # Master Hub & Landing Page
    path('', core_views.home, name='home'),

    # Django Administration
    path('admin/', admin.site.urls),

    # Role-based Authentication
    path('accounts/login/', accounts_views.RoleLoginView.as_view(), name='login'),
    path('accounts/signup/', accounts_views.signup_view, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),

    # Domain Portals
    path('customers/', include('customers.urls')),
    path('restaurants/', include('restaurants.urls')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
