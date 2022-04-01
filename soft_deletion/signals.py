from django.conf import settings
from django.dispatch import receiver
from utils.email import send_email

from control.models import Control
from .api_views import soft_delete_signal
from parametres.templatetags.parametres_tags import get_support_email_item
from user_profiles.models import UserProfile


@receiver(soft_delete_signal, sender=Control)
def send_email_after_control_soft_delete(session_user, obj, *args, **kwargs):
    """
    After a control is soft-deleted, we send an email to the inspector team.
    """
    control = obj
    inspectors = control.user_profiles.filter(profile_type=UserProfile.INSPECTOR)
    inspectors_emails = inspectors.values_list('user__email', flat=True)
    context = {
        'deleter_user': session_user,
        'control': control,
        'inspectors': inspectors,
        'support_team_email': get_support_email_item()["url"],
    }
    subject = f"collecte-pro - Suppression de l'espace - {control.title_display}"

    send_email(
        to=inspectors_emails,
        subject=subject,
        html_template='soft_deletion/email_delete_control.html',
        text_template='soft_deletion/email_delete_control.txt',
        extra_context=context,
    )
