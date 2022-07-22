from decimal import Decimal

from rest_framework import serializers
from .models import VideoModel


class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoModel
        fields = ['id', 'title', 'file']


class VideoListSerializer(serializers.ModelSerializer):
    video_charge = serializers.ReadOnlyField(source='ref_charge.charge', allow_null=True)

    class Meta:
        model = VideoModel
        fields = '__all__'


class TestVideoChargerSerializer(serializers.Serializer):
    video_choices = (
        ("mp4", "mp4"),
        ("mkv", "mkv"),
    )
    video_type = serializers.ChoiceField(choices=video_choices)
    video_size = serializers.IntegerField()
    video_length = serializers.IntegerField()
    video_charge = serializers.DecimalField(max_digits=9, decimal_places=1, default=Decimal("0.00"), read_only=True)

    def validate(self, attrs):
        if attrs['video_size'] == 0 or attrs['video_length'] == 0:
            raise serializers.ValidationError({
                "error": "Video Size or Video Length can't be blank"
            })
        if attrs['video_size'] < 500 * 1024 * 1024 and attrs['video_length'] < 378:
            attrs['video_charge'] = 5 + 12.5
        elif attrs['video_size'] < 500 * 1024 * 1024 and attrs['video_length'] > 378:
            attrs['video_charge'] = 5 + 20
        elif attrs['video_size'] > 500 * 1024 * 1024 and attrs['video_length'] > 378:
            attrs['video_charge'] = 12.5 + 20
        elif attrs['video_size'] > 500 * 1024 * 1024 and attrs['video_length'] < 378:
            attrs['video_charge'] = 12.5 + 12.5
        else:
            raise serializers.ValidationError({
                "error": "Incorrect video size or length"
            })
        return attrs
