from django.urls import path
from rest_framework import routers
from .views import VideoUploadAPIViewSet, CheckChargeForVideoAPIView

router = routers.DefaultRouter(trailing_slash=False)
router.register('video', VideoUploadAPIViewSet)

urlpatterns = [
    path('video-charge', CheckChargeForVideoAPIView.as_view())
              ] + router.urls
