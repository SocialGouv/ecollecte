from django import template

from parametres.models import Parametre

register = template.Library()

@register.simple_tag
def get_liens_footer_items():
    return Parametre.objects.filter(code="LIEN_FOOTER").order_by("ordre")

@register.simple_tag
def get_logo_footer_item():
    return Parametre.objects.filter(code="LOGO_FOOTER").first() or {
        "url": "img/logo-footer.png",
        "title": "Logo Marianne",
    }

@register.simple_tag
def get_entity_picture_item():
    return Parametre.objects.filter(code="ENTITY_PICTURE").first() or {
        "url": "img/picture-Republique-francaise.png",
        "title": "Logo Marianne",
    }