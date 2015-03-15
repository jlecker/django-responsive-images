from django import template

from ..utils import get_sized_image, get_sized_images


register = template.Library()


class SrcSetNode(template.Node):
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        tag = bits[0]
        image = bits[1]
        sizes = []
        try:
            for size in bits[2:-1]:
                sizes.append(tuple(map(int, size.split('x'))))
        except ValueError:
            raise template.TemplateSyntaxError(
                'Size must be specified as WxH.'
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
                        'Invalid crop specification.'
                    )
                else:
                    for crop_dim in crop:
                        if crop_dim > 100 or crop_dim < 0:
                            raise template.TemplateSyntaxError(
                                'Crop percent must be between 0 and 100.'
                            )
        else:
            crop = (50, 50)
        return cls(tag, image, sizes, crop)
    
    def __init__(self, tag, image, sizes, crop):
        self.tag = tag
        self.image = template.Variable(image)
        self.sizes = sizes
        self.crop = crop
    
    def render(self, context):
        image = self.image.resolve(context)
        resized_list = get_sized_images(image, self.sizes, self.crop)
        if self.tag == 'src':
            return resized_list[0].image_file.url
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

register.tag('src', SrcSetNode.handle_token)
register.tag('srcset', SrcSetNode.handle_token)
