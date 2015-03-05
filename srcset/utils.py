import os
from StringIO import StringIO

from django.core.files import File
from django.core.files.storage import default_storage

from PIL import Image, ImageOps

from .models import OriginalImage, ResizedImage


def get_sized_image(image, width, height, crop=True):
    (orig, c) = OriginalImage.objects.get_or_create(image_file=image.name)
    if width >= image.width:
        return orig
    image.open()
    orig_image = Image.open(image)
    if crop:
        new_image = ImageOps.fit(
            orig_image,
            (width, height),
            method=Image.BICUBIC
        )
        crop_type = 'center'
    else:
        orig_aspect = image.width / float(image.height)
        req_aspect = width / float(height)
        if orig_aspect > req_aspect:
            ratio = width / float(image.width)
        else:
            ratio = height / float(image.height)
        width = int(image.width * ratio + 0.5)
        height = int(image.height * ratio + 0.5)
        new_image = orig_image.resize((width, height), resample=Image.BICUBIC)
        crop_type = 'nocrop'
    image.close()
    data = StringIO()
    new_image.save(data, orig_image.format)
    split_ext = image.name.rsplit('.', 1)
    if len(split_ext) > 1:
        ext = split_ext[-1]
    else:
        ext = ''
    resized_path = default_storage.save(
        os.path.join(
            'resized_images',
            image.name,
            '{}x{}_{}.{}'.format(width, height, crop_type, ext)),
        File(data)
    )
    resized = ResizedImage.objects.create(
        original=orig,
        image_file=resized_path
    )
    return resized
