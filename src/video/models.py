import os
from decimal import Decimal

import cv2
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator
from django.db import models


def validate_file_size(file):
    file_size = file.size
    limit_KB_size = settings.MAX_UPLOAD_SIZE
    if file_size > limit_KB_size:
        # converting into KB
        f = limit_KB_size / 1024
        # converting into MB
        f = f / 1024
        # Converting into GB
        f = f / 1024
        raise ValidationError("Max size of file is %s GB" % f)


def get_video_length(video):
    # create video capture object
    data = cv2.VideoCapture(str(video))

    # count the number of frames
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = int(data.get(cv2.CAP_PROP_FPS))

    # calculate duration of the video
    seconds = int(frames / fps)
    return seconds


def delete_storage_file(file):
    path = os.path.abspath(file)
    os.remove(path)
    print("Removed Successfully!")


class DateTimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class VideoModel(DateTimeModel):
    title = models.CharField(max_length=50, help_text="Video Title")
    file = models.FileField(upload_to='videos', validators=[validate_file_size,
                                                            FileExtensionValidator(allowed_extensions=['mp4', 'mkv'])],
                            help_text="Video File should have mp4 or mkv extension and should not exceed 1 GB")
    video_length = models.IntegerField(help_text="Video Duration in seconds")
    video_size = models.DecimalField(max_digits=9, decimal_places=2, help_text="Video Size in bytes")
    ref_charge = models.ForeignKey('VideoCharge', on_delete=models.CASCADE, null=True, help_text="Video Charge")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file:

            file = self.file
            file_name = default_storage.save(file.name, file)

            #  Reading files from storage
            new_file = default_storage.open(file_name)

            video_length = get_video_length(new_file)

            # try:
            #     delete_storage_file(file_name)
            # except Exception as e:
            #     raise ValidationError({
            #         "error": f"{str(e)}"
            #     })
            if video_length > 10 * 60:
                raise ValidationError({
                    "error": "Video Cannot exceed 10 minutes of length"
                })
            else:
                self.video_size = self.file.size
                self.video_length = video_length

                if self.video_size < 500 * 1024 * 1024 and video_length < 378:
                    charge_obj = VideoCharge.objects.create(
                        charge=5 + 12.5
                    )
                    self.ref_charge = charge_obj
                elif self.video_size < 500 * 1024 * 1024 and video_length > 378:
                    charge_obj = VideoCharge.objects.create(
                        charge=12.5 + 20
                    )
                    self.ref_charge = charge_obj
                super(VideoModel, self).save(*args, **kwargs)


class VideoCharge(DateTimeModel):
    charge = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return self.charge
