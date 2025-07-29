from django import template
from store.models import Price

register = template.Library()

@register.filter
def get_item(dictionary, key):
    # Ensure dictionary is a dict; return 0 if invalid
    if not isinstance(dictionary, dict):
        return 0
    return dictionary.get(str(key), 0)

@register.filter
def to_price(price_id):
    try:
        return Price.objects.get(pk=price_id)
    except Price.DoesNotExist:
        return None