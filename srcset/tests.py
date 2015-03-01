import os

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.template import Context, Template
from django.test import TestCase

from .models import OriginalImage, ResizedImage
from .utils import get_sized_image


class SrcsetTests(TestCase):
    def setUp(self):
        src = os.path.join(
            os.path.dirname(__file__),
            'test_media',
            'image1.jpg'
        )
        with open(src, 'rb') as src_file:
            orig_path = default_storage.save(
                os.path.join('test_images', 'image1.jpg'),
                ImageFile(src_file)
            )
        self.orig = OriginalImage.objects.create(image_file=orig_path)
    
    def test_original(self):
        # verify size of original
        self.assertEqual(self.orig.image_file.width, 2688)
        # verify that the same object is found the next time
        (orig, created) = OriginalImage.objects.get_or_create(
            image_file=self.orig.image_file.name
        )
        self.assertFalse(created)
        self.assertEqual(orig, self.orig)
        self.assertEqual(OriginalImage.objects.count(), 1)
    
    def test_resized_width(self):
        resized = get_sized_image(self.orig.image_file, 500)
        self.assertEqual(OriginalImage.objects.count(), 1)
        self.assertEqual(
            OriginalImage.objects.get().width,
            self.orig.image_file.width
        )
        self.assertEqual(ResizedImage.objects.count(), 1)
        self.assertEqual(resized.width, 500)
        self.assertEqual(
            resized.image_file.name,
            'resized_images/test_images/image1.jpg',
            'Resized images should be saved under resized_images based on their original path.'
        )
    
    def tearDown(self):
        for image in OriginalImage.objects.all():
            image.image_file.delete(save=False)
        for image in ResizedImage.objects.all():
            image.image_file.delete(save=False)
        #os.rmdir(os.path.join(settings.MEDIA_ROOT, 'test_images'))
        #os.rmdir(os.path.join(settings.MEDIA_ROOT, 'resized_images', 'test_images'))
