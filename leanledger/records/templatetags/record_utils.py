from django import template


register = template.Library()


def absolute(value):
    return abs(value)


register.filter('absolute', absolute)
