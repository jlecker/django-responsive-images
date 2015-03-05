from distutils.core import setup

import srcset


setup(
    name='django-srcset',
    version=srcset.__version__,
    author='James Lecker Jr',
    author_email='james@convectivesoftware.com',
    url='https://github.com/ConvectiveSoftware/django-srcset',
    description='An Django app for resizing images and generating src and srcset attributes in HTML templates.',
    packages=['srcset'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
