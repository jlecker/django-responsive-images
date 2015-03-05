from django import template

from ..utils import get_sized_image


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
            crop = None
        else:
            (tag, image, size, crop) = bits
            if crop not in ['crop', 'nocrop']:
                raise template.TemplateSyntaxError(
                    'If given, last argument must specify crop options.'
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
        if crop == 'nocrop':
            self.crop = False
        else:
            self.crop = True
    
    def render(self, context):
        image = self.image.resolve(context)
        return get_sized_image(
            image,
            self.width,
            self.height,
            self.crop
        ).image_file.url


register.tag('src', SrcNode.handle_token)
