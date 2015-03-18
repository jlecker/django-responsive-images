Django Responsive Images
========================

A Django app for resizing images and generating src and srcset values
via template tags. It is intended to be very easy-to-use; just drop it
in and use the template tags.

Requires Django and Pillow.


Installation
------------

Install via pip::
	
	pip install django-responsive-images
	
Then add ``responsive_images`` to your INSTALLED_APPS.


Usage
-----

For the most part, this app is intended to be used via template tags.
A demonstation of currently supported functionality follows::

	{% load responsive_images %}

	{# resize and crop an image attached to instance to fit 500x500 #}
	<img src="{% src instance.image_field 500x500 %}">

	{# resize (without cropping) to fit 500x500 #}
	{# note: resulting size will likely not match both dimensions #}
	<img src="{% src instance.image_field 500x500 nocrop %}">
	
	{# specify crop position as percent: X,Y #}
	<img src="{% src instance.image_field 500x500 50,20 %}">
	
	{# center crop is the default, all of these are equivalent #}
	<img src="{% src instance.image_field 500x500 %}">
	<img src="{% src instance.image_field 500x500 crop %}">
	<img src="{% src instance.image_field 500x500 center %}">
	<img src="{% src instance.image_field 500x500 50,50 %}">
	
	{# resize image multiple times and create srcset #}
	<img srcset="{% srcset instance.field 400x400 800x800 1600x1600 %}">
	
	{# srcset also allows nocrop and crop position #}
	<img srcset="{% srcset instance.field 400x400 800x800 nocrop %}">
	<img srcset="{% srcset instance.field 400x400 800x800 50,20 %}">

Note: If a specified size is larger than the source image in one or both
dimensions, the resulting image will not match the specified size. Images
will never be upscaled. The resulting image may be resized in only one
dimension (if cropping) or it may return the original image. In either
case, the srcset tag will output the correct width for the image used.
