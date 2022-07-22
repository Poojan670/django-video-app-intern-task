from django.urls import path, include

urlpatterns = [
    path('video-app/', include('src.video.urls'))
]