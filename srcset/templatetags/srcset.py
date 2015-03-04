from django import template

from ..utils import get_sized_image


register = template.Library()


@register.simple_tag
def src(image, size):
    try:
        (width, height) = map(int, size.split('x'))
    except ValueError:
        raise template.TemplateSyntaxError(
            'Second argument must be WxH.'
        )
    if not image:
        return ''
    resized = get_sized_image(image, width, height)
    return resized.image_file.url
