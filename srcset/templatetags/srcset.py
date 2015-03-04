from django import template

from ..utils import get_sized_image


register = template.Library()


class SrcNode(template.Node):
    @classmethod
    def handle_token(cls, parser, token):
        try:
            (tag, image, size) = token.split_contents()
        except ValueError:
            raise template.TemplateSyntaxError(
                '{} takes image and size arguments'.format(
                    token.contents.split()[0]
                )
            )
        try:
            (width, height) = map(int, size.split('x'))
        except ValueError:
            raise template.TemplateSyntaxError(
                'Second argument must be WxH.'
            )
        return cls(image, width, height)
    
    def __init__(self, image, width, height):
        self.image = template.Variable(image)
        self.width = width
        self.height = height
    
    def render(self, context):
        image = self.image.resolve(context)
        return get_sized_image(image, self.width, self.height).image_file.url


register.tag('src', SrcNode.handle_token)
