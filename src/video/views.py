from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from .serializers import (VideoUploadSerializer, VideoListSerializer,
                          TestVideoChargerSerializer)
from .models import VideoModel
import django_filters


class VideoListFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_at')

    class Meta:
        model = VideoModel
        fields = ['id', 'date', 'title', 'created_at']


class VideoUploadAPIViewSet(viewsets.ModelViewSet):
    queryset = VideoModel.objects.all().order_by('id')
    serializer_class = VideoUploadSerializer
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    filterset_class = VideoListFilterSet
    search_fields = ['id', 'title']
    ordering_fields = ['id']

    def get_serializer_class(self):
        if self.request.method == "GET":
            return VideoListSerializer
        return self.serializer_class


class CheckChargeForVideoAPIView(generics.CreateAPIView):
    serializer_class = TestVideoChargerSerializer

    def post(self, request, *args, **kwargs):
        serializer = TestVideoChargerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({
                "data": serializer.data,
                "The total charge for your video will be ": serializer.data['video_charge'] + " Rs"
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
