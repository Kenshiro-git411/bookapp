from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# division_by_zero = 1 / 0

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
    # path('sentry-debug/', division_by_zero),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # settings.pyファイルのMEDIA_URLで指定してあるURLが入力されると、同じくsettings.pyファイルのMEDIA_ROOTで指定されているフォルダから画像を呼び出してくる。

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)