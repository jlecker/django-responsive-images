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
    
    def test_resize_one(self):
        resized = get_sized_image(self.orig1.image_file, (500, 500))
        self.assertEqual(OriginalImage.objects.count(), 2)
        self.assertEqual(ResizedImage.objects.count(), 1)
        self.assertEqual(
            resized.image_file.name,
            os.path.join(
                'resized_images',
                'test_images',
                'image1.jpg',
                '500x500_center.jpg'
            )
        )

    def test_resize_one_nocrop(self):
        # constrained by width
        r1 = get_sized_image(self.orig1.image_file, (400, 600), crop=False)
        self.assertEqual(r1.size, (400, 226))
        # constrained by height
        r2 = get_sized_image(self.orig1.image_file, (400, 200), crop=False)
        self.assertEqual(r2.size, (354, 200))
    
    def test_resize_larger(self):
        r1 = get_sized_image(self.orig2.image_file, (500, 500))
        self.assertFalse(ResizedImage.objects.exists())
        self.assertEqual(r1.size, (300, 170))
        self.assertEqual(
            r1.image_file.name,
            os.path.join(
                'test_images',
                'image2.jpg'
            )
        )
    
    def test_resize_cases(self):
        r1 = get_sized_image(self.orig2.image_file, (200, 200))
        self.assertEqual(r1.size, (200, 170))
        self.assertTrue(r1.image_file.name.endswith('200x170_center.jpg'))
        r2 = get_sized_image(self.orig2.image_file, (300, 150))
        self.assertEqual(r2.size, (300, 150))
        self.assertTrue(r2.image_file.name.endswith('300x150_center.jpg'))
        r3 = get_sized_image(self.orig2.image_file, (200, 200), crop=False)
        self.assertEqual(r3.size, (200, 113))
        self.assertTrue(r3.image_file.name.endswith('200x113_nocrop.jpg'))
        r4 = get_sized_image(self.orig2.image_file, (300, 150), crop=False)
        self.assertEqual(r4.size, (265, 150))
        self.assertTrue(r4.image_file.name.endswith('265x150_nocrop.jpg'))
    
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
                '500x500_center.jpg'
            )
        )
        self.assertEqual(ResizedImage.objects.count(), 1)
        r1 = ResizedImage.objects.get()
        self.assertEqual(r1.size, (500, 500))
    
    def test_src_tag_nocrop(self):
        template = Template('{% load srcset %}{% src image 500x500 nocrop %}')
        context = Context({'image': self.orig1.image_file})
        rendered = template.render(context)
        self.assertEqual(
            rendered,
            os.path.join(
                settings.MEDIA_URL,
                'resized_images',
                'test_images',
                'image1.jpg',
                '500x283_nocrop.jpg'
            )
        )
        r1 = ResizedImage.objects.get()
        self.assertEqual(r1.size, (500, 283))
    
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
