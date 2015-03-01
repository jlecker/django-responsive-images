from django import template

from ..utils import get_sized_image


register = template.Library()


@register.simple_tag
def src(image, size):
    try:
        width = int(size)
    except ValueError:
        raise template.TemplateSyntaxError(
            'Second argument must be width.'
        )
    if not image:
        return ''
    resized = get_sized_image(image, width)
    return resized.image_file.url
