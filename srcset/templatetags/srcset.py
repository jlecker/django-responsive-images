from django import template

from ..utils import get_sized_image, get_sized_images


register = template.Library()


class SrcNode(template.Node):
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        if len(bits) not in [3, 4]:
            raise template.TemplateSyntaxError(
                'Arguments are image, size, [crop].'
            )
        if len(bits) == 3:
            (tag, image, size) = bits
            crop = (50, 50)
        else:
            (tag, image, size, crop) = bits
            if crop in ['crop', 'center']:
                crop = (50, 50)
            elif crop == 'nocrop':
                crop = None
            else:
                try:
                    crop = tuple(map(int, crop.split(',')))
                except ValueError:
                    raise template.TemplateSyntaxError(
                        'If given, last argument must specify crop.'
                    )
                else:
                    for crop_dim in crop:
                        if crop_dim > 100 or crop_dim < -100:
                            raise template.TemplateSyntaxError(
                                'Invalid crop percentage.'
                            )
        try:
            (width, height) = map(int, size.split('x'))
        except ValueError:
            raise template.TemplateSyntaxError(
                'Second argument must be WxH.'
            )
        return cls(image, width, height, crop)
    
    def __init__(self, image, width, height, crop):
        self.image = template.Variable(image)
        self.width = width
        self.height = height
        self.crop = crop
    
    def render(self, context):
        image = self.image.resolve(context)
        return get_sized_image(
            image,
            (self.width, self.height),
            self.crop
        ).image_file.url

register.tag('src', SrcNode.handle_token)


class SrcSetNode(template.Node):
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        image = bits[1]
        sizes = []
        try:
            for size in bits[2:-1]:
                sizes.append(tuple(map(int, size.split('x'))))
        except ValueError:
            raise template.TemplateSyntaxError(
                'Sizes must be specified as WxH.'
            )
        try:
            sizes.append(tuple(map(int, bits[-1].split('x'))))
        except ValueError:
            if bits[-1] in ['crop', 'center']:
                crop = (50, 50)
            elif bits[-1] == 'nocrop':
                crop = None
            else:
                try:
                    crop = tuple(map(int, bits[-1].split(',')))
                except ValueError:
                    raise template.TemplateSyntaxError(
                        'If not a size, last argument must specify crop.'
                    )
                else:
                    for crop_dim in crop:
                        if crop_dim > 100 or crop_dim < 100:
                            raise template.TemplateSyntaxError(
                                'Invalid crop percentage.'
                            )
        else:
            crop = (50, 50)
        return cls(image, sizes, crop)
    
    def __init__(self, image, sizes, crop):
        self.image = template.Variable(image)
        self.sizes = sizes
        self.crop = crop
    
    def render(self, context):
        image = self.image.resolve(context)
        resized_list = get_sized_images(image, self.sizes, self.crop)
        srcset = ''
        last_width = 0
        for resized in resized_list:
            if resized.width != last_width:
                srcset += '{} {}w, '.format(
                    resized.image_file.url,
                    resized.width
                )
                last_width = resized.width
        else:
            srcset = srcset[:-2]
        return srcset

register.tag('srcset', SrcSetNode.handle_token)
