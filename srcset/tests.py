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
        self.orig1 = _create_original('image1.jpg') # 2688x1520
        self.orig2 = _create_original('image2.jpg') # 300x170
    
    def test_resize(self):
        resized = get_sized_image(self.orig1.image_file, 500, 500)
        self.assertEqual(OriginalImage.objects.count(), 2)
        self.assertEqual(ResizedImage.objects.count(), 1)
        self.assertEqual(
            resized.image_file.name,
            os.path.join(
                'resized_images',
                'test_images',
                'image1.jpg',
                '500x500.jpg'
            )
        )

    def notest_resize_smaller_nocrop(self):
        # constrained by width
        resized1 = get_sized_image(self.orig1.image_file, 400, 600)
        self.assertEqual(resized1.width, 400)
        self.assertEqual(resized1.width, 226)
        # constrained by height
        resized2 = get_sized_image(self.orig1.image_file, 400, 200)
        self.assertEqual(resized2.width, 354)
        self.assertEqual(resized2.width, 200)
    
    def test_resize_larger(self):
        resized = get_sized_image(self.orig2.image_file, 500, 500)
        self.assertFalse(ResizedImage.objects.exists())
        self.assertEqual(resized.width, 300)
        self.assertEqual(resized.height, 170)
        self.assertEqual(
            resized.image_file.name,
            os.path.join(
                'test_images',
                'image2.jpg'
            )
        )
    
    def test_src_tag(self):
        template = Template('{% load srcset %}{% src image 500x500 %}')
        context = Context({'image': self.orig1.image_file})
        rendered = template.render(context)
        self.assertEqual(
            rendered,
            os.path.join(
                settings.MEDIA_URL,
                'resized_images',
                'test_images',
                'image1.jpg',
                '500x500.jpg'
            )
        )
        self.assertEqual(ResizedImage.objects.count(), 1)
        self.assertEqual(ResizedImage.objects.get().width, 500)
        self.assertEqual(ResizedImage.objects.get().height, 500)
    
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
