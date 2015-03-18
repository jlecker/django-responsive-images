from distutils.core import setup
import os

import responsive_images


if os.path.exists('README.rst'):
    with open('README.rst') as readme:
        long_desc = readme.read()
else:
    long_desc = ''

setup(
    name='django-responsive-images',
    version=responsive_images.__version__,
    author='James Lecker Jr',
    author_email='james@convectivesoftware.com',
    url='https://github.com/ConvectiveSoftware/django-responsive-images',
    description='A Django app for resizing images and generating src and srcset values via template tags.',
    long_description = long_desc,
    download_url='https://github.com/ConvectiveSoftware/django-responsive-images/tarball/{}'.format(responsive_images.__version__),
    packages=['responsive_images', 'responsive_images.templatetags'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
