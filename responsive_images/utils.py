import os
from StringIO import StringIO

from django.core.files import File
from django.core.files.storage import default_storage

from PIL import Image, ImageOps

from .models import OriginalImage, ResizedImage


def get_sized_images(image, sizes, crop=(50, 50)):
    (orig, c) = OriginalImage.objects.get_or_create(image_file=image.name)
    
    # filter out duplicates and larger than original
    sizes_set = set()
    for (width, height) in sizes:
        width = min(width, image.width)
        height = min(height, image.height)
        sizes_set.add((width, height))
    sizes = sorted(sizes_set)
    
    if sizes[0] == orig.size:
        # smallest size is original image
        return [orig]
    
    # common info to all resized images
    if crop:
        crop_type = '{}-{}'.format(*crop)
    else:
        crop_type = 'nocrop'
    split_ext = image.name.rsplit('.', 1)
    if len(split_ext) > 1:
        ext = '.' + split_ext[-1]
    else:
        ext = ''
    
    # open the original image
    image.open()
    orig_image = Image.open(image)
    orig_image.load()
    image.close()
    
    # create the resized images
    resized = []
    for (width, height) in sizes:
        if (width, height) == (image.width, image.height):
            resized.append(orig)
            continue
        try:
            found = ResizedImage.objects.get(
                original=orig,
                width=width,
                height=height,
                crop=crop_type
            )
        except ResizedImage.DoesNotExist:
            pass
        else:
            resized.append(found)
            continue
        
        if crop:
            new_image = ImageOps.fit(
                orig_image,
                (width, height),
                method=Image.BICUBIC,
                centering=(crop[0] / 100.0, crop[1] / 100.0)
            )
        else:
            orig_aspect = image.width / float(image.height)
            req_aspect = width / float(height)
            if orig_aspect > req_aspect:
                ratio = width / float(image.width)
            else:
                ratio = height / float(image.height)
            width = int(image.width * ratio + 0.5)
            height = int(image.height * ratio + 0.5)
            
            new_image = orig_image.resize(
                (width, height),
                resample=Image.BICUBIC
            )
        
        data = StringIO()
        new_image.save(data, orig_image.format)
        resized_path = default_storage.save(
            os.path.join(
                'responsive_images',
                image.name,
                '{}x{}_{}{}'.format(width, height, crop_type, ext)),
            File(data)
        )
        resized.append(ResizedImage.objects.create(
            original=orig,
            image_file=resized_path,
            crop=crop_type
        ))
    
    return resized


def get_sized_image(image, size, crop=(50, 50)):
    return get_sized_images(image, [size], crop)[0]
