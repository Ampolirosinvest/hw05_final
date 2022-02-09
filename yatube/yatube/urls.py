"""yatube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('posts.urls', namespace='posts')),
    # path('group/<slug:slug>/', include('posts.urls', namespace = 'posts')),
    path('admin/', admin.site.urls),
    # добавил перед основным
    path('auth/', include('users.urls', namespace='users')),
    # подключил подкапотную аутентификацию
    path('auth/', include('django.contrib.auth.urls')),
    # подбавил ститику
    path('about/', include('about.urls', namespace='about')),
]

# Подвяжем хендлер к view функции page_not_found в приложении core
handler404 = 'core.views.page_not_found'
handler403 = 'core.views.page_forbidden'
handler500 = 'core.views.page_internal_server_error'

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
