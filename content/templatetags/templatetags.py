from django import template
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

register = template.Library()


@register.simple_tag
def mediapath(image_path):
    return f'/media/{image_path}'


@register.filter
def mediapath(image_path):
    return f'/media/{image_path}'

