from django import template
from rango.models import Category

register = template.Library()

@register.inclusion_tag('rango/cats.html')
# This method returns the list of categories, it's linked up with rango/cats.html template
def get_category_list(cat=None):
    return {'cats': Category.objects.all(),
            'act_cat': cat}