import os

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.template import Context, Template
from django.test import TestCase

from .models import OriginalImage, ResizedImage


class TemplateTagTests(TestCase):
    def setUp(self):
        src = os.path.join(
            os.path.dirname(__file__),
            'test_media',
            'image1.jpg'
        )
        with open(src, 'rb') as f:
            self.orig = default_storage.save('testimage1.jpg', File(f))
    
    def test_src_width(self):
        t = Template('{% load srcset %}{% src image 500 %}')
        c = Context({'image', self.orig})
        #self.assertEqual(OriginalImage.objects.count(), 1)
        #self.assertEqual(ResizedImage.objects.count(), 1)
    
    def tearDown(self):
        default_storage.delete(self.orig)
        for image in OriginalImage.objects.all():
            image.image_file.delete(save=False)
        for image in ResizedImage.objects.all():
            self.orig.image_file.delete(save=False)
