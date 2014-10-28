from django import template

register = template.Library()

def lastn(value, n):
    try:
        return value[:n]
    except:
        return value

register.filter('lastn', lastn)
