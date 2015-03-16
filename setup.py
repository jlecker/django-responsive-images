from distutils.core import setup

import responsive_images


setup(
    name='django-responsive-images',
    version=responsive_images.__version__,
    author='James Lecker Jr',
    author_email='james@convectivesoftware.com',
    url='https://github.com/ConvectiveSoftware/django-responsive-images',
    description='An Django app for resizing images and generating src and srcset attributes via template tags.',
    download_url='https://github.com/ConvectiveSoftware/django-responsive-images/tarball/{}'.format(responsive_images.__version__),
    packages=['responsive_images', 'responsive_images.templatetags'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
