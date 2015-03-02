import os

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.template import Context, Template
from django.test import TestCase

from .models import OriginalImage, ResizedImage
from .utils import get_sized_image


def _create_original(name):
    src = os.path.join(
        os.path.dirname(__file__),
        'test_media',
        name
    )
    with open(src, 'rb') as src_file:
        orig_path = default_storage.save(
            os.path.join('test_images', name),
            ImageFile(src_file)
        )
    return OriginalImage.objects.create(image_file=orig_path)


def _clean_up_directory(path):
    try:
        os.rmdir(path)
    except OSError:
        pass


class SrcsetTests(TestCase):
    def setUp(self):
        self.orig1 = _create_original('image1.jpg')
        self.orig2 = _create_original('image2.jpg')
    
    def test_resize_width_smaller(self):
        resized = get_sized_image(self.orig1.image_file, 500)
        # verify no additional OriginalImage
        self.assertEqual(OriginalImage.objects.count(), 2)
        self.assertEqual(ResizedImage.objects.count(), 1)
        self.assertEqual(resized.width, 500)
        self.assertEqual(
            resized.image_file.name,
            os.path.join(
                'resized_images',
                'test_images',
                'image1.jpg',
                '500.jpg'
            )
        )
    
    def test_resize_width_larger(self):
        resized = get_sized_image(self.orig2.image_file, 500)
        self.assertFalse(ResizedImage.objects.exists())
        self.assertEqual(resized.width, 300)
        self.assertEqual(
            resized.image_file.name,
            os.path.join(
                'test_images',
                'image2.jpg'
            )
        )
    
    def test_src_width(self):
        template = Template('{% load srcset %}{% src image 500 %}')
        context = Context({'image': self.orig1.image_file})
        rendered = template.render(context)
        self.assertEqual(
            rendered,
            os.path.join(
                settings.MEDIA_URL,
                'resized_images',
                'test_images',
                'image1.jpg',
                '500.jpg'
            )
        )
        self.assertEqual(ResizedImage.objects.count(), 1)
        r = ResizedImage.objects.get()
        self.assertEqual(r.width, 500)
    
    def tearDown(self):
        for image in OriginalImage.objects.all():
            image.image_file.delete(save=False)
        for image in ResizedImage.objects.all():
            image.image_file.delete(save=False)
        _clean_up_directory(os.path.join(settings.MEDIA_ROOT, 'test_images'))
        _clean_up_directory(os.path.join(
            settings.MEDIA_ROOT,
            'resized_images',
            'test_images',
            'image1.jpg'
        ))
        _clean_up_directory(os.path.join(
            settings.MEDIA_ROOT,
            'resized_images',
            'test_images',
            'image2.jpg'
        ))
        _clean_up_directory(os.path.join(
            settings.MEDIA_ROOT,
            'resized_images',
            'test_images'
        ))
