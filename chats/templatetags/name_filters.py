from django import template

register = template.Library()

@register.filter
def first_char(value):
    return value[0] if value else ""