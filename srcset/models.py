from django.db import models


class OriginalImage(models.Model):
    image_file = models.ImageField(
        height_field='height',
        width_field='width',
        db_index=True
    )
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()


class ResizedImage(models.Model):
    original = models.ForeignKey(OriginalImage, db_index=True)
    image_file = models.ImageField(
        upload_to='resized_images',
        height_field='height',
        width_field='width',
    )
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    crop = models.CharField(max_length=10)
