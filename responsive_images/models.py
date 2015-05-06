from django.db import models


class ImageModel(models.Model):
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    
    class Meta:
        abstract = True
    
    @property
    def size(self):
        return (self.width, self.height)


class OriginalImage(ImageModel):
    image_file = models.ImageField(
        upload_to='original_images', # required for Django 1.6, but not used
        height_field='height',
        width_field='width',
        db_index=True
    )


class ResizedImage(ImageModel):
    original = models.ForeignKey(OriginalImage, db_index=True)
    image_file = models.ImageField(
        upload_to='responsive_images',
        height_field='height',
        width_field='width',
    )
    crop = models.CharField(max_length=10)
    
    class Meta:
        unique_together = ('original', 'width', 'height', 'crop')
