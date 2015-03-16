import os

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.template import Context, Template
from django.test import TestCase

from .models import OriginalImage, ResizedImage
from .utils import get_sized_image, get_sized_images


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
        r1 = get_sized_image(self.orig1.image_file, (500, 500))
        self.assertEqual(OriginalImage.objects.count(), 2)
        self.assertEqual(ResizedImage.objects.count(), 1)
        self.assertEqual(r1.image_file.name, os.path.join(
            'responsive_images',
            self.orig1.image_file.name,
            '500x500_50-50.jpg'
        ))
    
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
        self.assertEqual(r1.image_file.name, self.orig2.image_file.name)
    
    def test_resize_cases(self):
        r1 = get_sized_image(self.orig2.image_file, (200, 200))
        self.assertEqual(r1.size, (200, 170))
        self.assertTrue(r1.image_file.name.endswith('200x170_50-50.jpg'))
        r2 = get_sized_image(self.orig2.image_file, (300, 150))
        self.assertEqual(r2.size, (300, 150))
        self.assertTrue(r2.image_file.name.endswith('300x150_50-50.jpg'))
        r3 = get_sized_image(self.orig2.image_file, (200, 200), crop=None)
        self.assertEqual(r3.size, (200, 113))
        self.assertTrue(r3.image_file.name.endswith('200x113_nocrop.jpg'))
        r4 = get_sized_image(self.orig2.image_file, (300, 150), crop=None)
        self.assertEqual(r4.size, (265, 150))
        self.assertTrue(r4.image_file.name.endswith('265x150_nocrop.jpg'))
    
    def test_resize_same(self):
        r1 = get_sized_image(self.orig1.image_file, (500, 500))
        r2 = get_sized_image(self.orig1.image_file, (500, 500))
        self.assertEqual(ResizedImage.objects.count(), 1)
        self.assertEqual(r1, r2)
    
    def test_resize_multiple(self):
        (r1, r2, r3) = get_sized_images(self.orig1.image_file, [
            (1000, 1000),
            (2000, 2000),
            (3000, 3000),
            (4000, 4000),
        ])
        self.assertEqual(OriginalImage.objects.count(), 2)
        self.assertEqual(ResizedImage.objects.count(), 2)
        self.assertEqual(r1.size, (1000, 1000))
        self.assertTrue(r1.image_file.name.endswith('1000x1000_50-50.jpg'))
        self.assertEqual(r2.size, (2000, 1520))
        self.assertTrue(r2.image_file.name.endswith('2000x1520_50-50.jpg'))
        self.assertEqual(r3.size, (2688, 1520))
        self.assertEqual(r3.image_file.name, self.orig1.image_file.name)
    
    def test_resize_multiple_nocrop(self):
        (r1, r2, r3) = get_sized_images(self.orig1.image_file, [
            (1000, 1000),
            (2000, 2000),
            (3000, 3000),
            (4000, 4000),
        ], crop=None)
        self.assertEqual(r1.size, (1000, 565))
        self.assertTrue(r1.image_file.name.endswith('1000x565_nocrop.jpg'))
        self.assertEqual(r2.size, (2000, 1131))
        self.assertTrue(r2.image_file.name.endswith('2000x1131_nocrop.jpg'))
        self.assertEqual(r3.size, (2688, 1520))
        self.assertEqual(r3.image_file.name, self.orig1.image_file.name)
    
    def test_src_tag(self):
        template = Template('{% load responsive_images %}{% src image 500x500 %}')
        context = Context({'image': self.orig1.image_file})
        rendered = template.render(context)
        self.assertEqual(
            rendered,
            os.path.join(
                settings.MEDIA_URL,
                'responsive_images',
                self.orig1.image_file.name,
                '500x500_50-50.jpg'
            )
        )
        self.assertEqual(ResizedImage.objects.count(), 1)
        r1 = ResizedImage.objects.get()
        self.assertEqual(r1.size, (500, 500))
    
    def test_src_tag_nocrop(self):
        template = Template('{% load responsive_images %}{% src image 500x500 nocrop %}')
        context = Context({'image': self.orig1.image_file})
        rendered = template.render(context)
        self.assertEqual(
            rendered,
            os.path.join(
                settings.MEDIA_URL,
                'responsive_images',
                self.orig1.image_file.name,
                '500x283_nocrop.jpg'
            )
        )
        r1 = ResizedImage.objects.get()
        self.assertEqual(r1.size, (500, 283))
    
    def test_src_tag_crop(self):
        template1 = Template('{% load responsive_images %}{% src image 500x500 %}')
        template2 = Template('{% load responsive_images %}{% src image 500x500 crop %}')
        template3 = Template('{% load responsive_images %}{% src image 500x500 center %}')
        template4 = Template('{% load responsive_images %}{% src image 500x500 40,10 %}')
        context = Context({'image': self.orig1.image_file})
        rendered1 = template1.render(context)
        rendered2 = template2.render(context)
        rendered3 = template3.render(context)
        rendered4 = template4.render(context)
        self.assertEqual(ResizedImage.objects.count(), 2)
        center_crop_url = os.path.join(
            settings.MEDIA_URL,
            'responsive_images',
            self.orig1.image_file.name,
            '500x500_50-50.jpg'
        )
        self.assertEqual(rendered1, center_crop_url)
        self.assertEqual(rendered2, center_crop_url)
        self.assertEqual(rendered3, center_crop_url)
        self.assertEqual(rendered4, os.path.join(
            settings.MEDIA_URL,
            'responsive_images',
            self.orig1.image_file.name,
            '500x500_40-10.jpg'
        ))
        for resized in ResizedImage.objects.all():
            self.assertEqual(resized.size, (500, 500))
    
    def test_src_tag_same(self):
        template = Template('{% load responsive_images %}{% src image 500x500 %}')
        context = Context({'image': self.orig1.image_file})
        rendered1 = template.render(context)
        rendered2 = template.render(context)
        for rendered in [rendered1, rendered2]:
            self.assertEqual(
                rendered,
                os.path.join(
                    settings.MEDIA_URL,
                    'responsive_images',
                    self.orig1.image_file.name,
                    '500x500_50-50.jpg'
                )
            )
        self.assertEqual(ResizedImage.objects.count(), 1)
    
    def test_srcset_tag(self):
        template = Template('{% load responsive_images %}{% srcset image 1000x1000 2000x2000 3000x3000 4000x4000 %}')
        context = Context({'image': self.orig1.image_file})
        rendered = template.render(context)
        self.assertEqual(
            rendered,
            os.path.join(
                settings.MEDIA_URL,
                'responsive_images',
                self.orig1.image_file.name,
                '1000x1000_50-50.jpg'
            ) + ' 1000w, '
            + os.path.join(
                settings.MEDIA_URL,
                'responsive_images',
                self.orig1.image_file.name,
                '2000x1520_50-50.jpg'
            ) + ' 2000w, '
            + os.path.join(
                settings.MEDIA_URL,
                self.orig1.image_file.name,
            ) + ' 2688w'
        )
        self.assertEqual(ResizedImage.objects.count(), 2)
    
    def test_srcset_tag_nocrop(self):
        template = Template('{% load responsive_images %}{% srcset image 1000x1000 2000x2000 3000x3000 4000x4000 nocrop %}')
        context = Context({'image': self.orig1.image_file})
        rendered = template.render(context)
        self.assertEqual(
            rendered,
            os.path.join(
                settings.MEDIA_URL,
                'responsive_images',
                self.orig1.image_file.name,
                '1000x565_nocrop.jpg'
            ) + ' 1000w, '
            + os.path.join(
                settings.MEDIA_URL,
                'responsive_images',
                self.orig1.image_file.name,
                '2000x1131_nocrop.jpg'
            ) + ' 2000w, '
            + os.path.join(
                settings.MEDIA_URL,
                self.orig1.image_file.name,
            ) + ' 2688w'
        )
        self.assertEqual(ResizedImage.objects.count(), 2)
    
    def test_srcset_tag_same_width(self):
        template = Template('{% load responsive_images %}{% srcset image 450x150 600x200 %}')
        context = Context({'image': self.orig2.image_file})
        rendered = template.render(context)
        self.assertEqual(
            rendered,
            os.path.join(
                settings.MEDIA_URL,
                'responsive_images',
                self.orig2.image_file.name,
                '300x150_50-50.jpg'
            ) + ' 300w'
        )
        self.assertEqual(ResizedImage.objects.count(), 1)
    
    def tearDown(self):
        for image in OriginalImage.objects.all():
            image.image_file.delete(save=False)
        for image in ResizedImage.objects.all():
            image.image_file.delete(save=False)
        _clean_up_directory(os.path.join(settings.MEDIA_ROOT, 'test_images'))
        _clean_up_directory(os.path.join(
            settings.MEDIA_ROOT,
            'responsive_images',
            self.orig1.image_file.name,
        ))
        _clean_up_directory(os.path.join(
            settings.MEDIA_ROOT,
            'responsive_images',
            self.orig2.image_file.name,
        ))
        _clean_up_directory(os.path.join(
            settings.MEDIA_ROOT,
            'responsive_images',
            'test_images'
        ))
