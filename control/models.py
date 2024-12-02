import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.apps import apps

from django_cleanup import cleanup
from model_utils.models import TimeStampedModel
from ordered_model.models import OrderedModel
from django_softdelete.models import SoftDeleteModel

from soft_deletion.managers import DeletableQuerySet

from .docx import DocxMixin
from .upload_path import questionnaire_file_path, question_file_path, response_file_path, questionnaire_pj_file_path, Prefixer

from user_profiles.models import UserProfile


class WithNumberingMixin(object):
    """
    Add an helper for getting the numbering base on the order field.
    """

    @property
    def numbering(self):
        return self.order + 1
    numbering.fget.short_description = 'Numérotation'


class FileInfoMixin(object):
    """
    Add common helpers for file information.
    """

    @property
    def control(self):
        if isinstance(self, QuestionFile):
            if not self.question:
                return None
            return self.question.control
        if not self.questionnaire:
            return None
        return self.questionnaire.control
        

    @property
    def questionnaire(self):
        if isinstance(self, QuestionFile):
            if not self.question:
                return None
            return self.question.questionnaire
        if not self.questionnnaire:
            return None
        return self.questionnaire

    @property
    def theme(self):
        if not self.question:
            return None
        return self.question.theme

    @property
    def file_name(self):
        return self.file.name

    def __str__(self):
        return f'id {self.id} - {self.file_name}'


class Control(SoftDeleteModel):
    # These error messages are used in the frontend (ConsoleCreate.vue),
    # if you change them you might break the frontend.
    INVALID_ERROR_MESSAGE = 'INVALID'
    UNIQUE_ERROR_MESSAGE = 'UNIQUE'

    title = models.CharField(
        "procédure",
        help_text="Procédure pour laquelle est ouvert cet espace de dépôt",
        max_length=255)
    depositing_organization = models.CharField(
        verbose_name="Organisme interrogé",
        help_text="Organisme qui va déposer les pièces dans cet espace de dépôt",
        max_length=255,
        blank=True,
    )
    reference_code = models.CharField(
        verbose_name="code de référence",
        max_length=30,
        help_text='Ce code est utilisé notamment pour le dossier de stockage des réponses',
        validators=[
            RegexValidator(
                regex=r'^[\.\s\w-]+$',
                message=INVALID_ERROR_MESSAGE,
            ),
        ],
        unique=True,
        error_messages={'unique': UNIQUE_ERROR_MESSAGE})

    is_model = models.BooleanField(
        verbose_name="Modèle",
        default=False,
        help_text="Indique si cette procédure est un modèle"
    )
    
    objects = DeletableQuerySet.as_manager()

    class Meta:
        verbose_name = "Procédure"
        verbose_name_plural = "Procédures"

    def data(self):
        return {
            'id': self.id,
            'title': self.title,
            'depositing_organization': self.depositing_organization,
            'is_model': self.is_model,
        }

    @property
    def next_questionnaire_numbering(self):
        if not self.questionnaires.exists():
            return 1
        return self.questionnaires.last().numbering + 1

    @property
    def has_multiple_inspectors(self):
        return self.access.filter(access_type='demandeur').count() > 1

    @property
    def title_display(self):
        if self.depositing_organization:
            return f'{self.title} - {self.depositing_organization}'
        return self.title

    def __str__(self):
        if self.depositing_organization:
            return f'[ID{self.id}] - {self.title} - {self.depositing_organization}'
        return f'[ID{self.id}] - {self.title}'


class Questionnaire(OrderedModel, WithNumberingMixin, DocxMixin):
    title = models.CharField("titre", max_length=255)
    sent_date = models.DateField(
        verbose_name="date d'envoi", blank=True, null=True,
        help_text="Date de transmission du questionnaire")
    end_date = models.DateField(
        verbose_name="échéance", blank=True, null=True,
        help_text="Date de réponse souhaitée")
    description = models.TextField("description", blank=True)
    editor = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, related_name='questionnaires', on_delete=models.PROTECT,
        blank=True, null=True)
    uploaded_file = models.FileField(
        verbose_name="fichier du questionnaire", upload_to=questionnaire_file_path,
        null=True, blank=True,
        help_text=(
            "Si ce fichier est renseigné, il sera proposé au téléchargement."
            "Sinon, un fichier généré automatiquement sera disponible."))
    generated_file = models.FileField(
        verbose_name="fichier du questionnaire généré automatiquement",
        upload_to=questionnaire_file_path,
        null=True, blank=True,
        help_text=(
            "Ce fichier est généré automatiquement quand le questionnaire est enregistré."))
    control = models.ForeignKey(
        to='Control', verbose_name='procédure', related_name='questionnaires',
        null=True, default=0, blank=True, on_delete=models.CASCADE)
    order_with_respect_to = 'control'
    order = models.PositiveIntegerField('order', db_index=True)
    is_draft = models.BooleanField(
        verbose_name="brouillon", default=False,
        help_text="Ce questionnaire est-il encore au stade de brouillon?")
    is_replied = models.BooleanField(
        verbose_name="répondu", default=False,
        help_text="Ce questionnaire a-t-il obtenu toutes les réponses de l'organisme répondant ?")
    is_finalized = models.BooleanField(
        verbose_name="finalisé", default=False,
        help_text="Ce questionnaire a-t-il été finalisé par le demandeur ?")
    modified = models.DateTimeField('modifié', auto_now=True, null=True)

    class Meta:
        ordering = ('control', 'order')
        verbose_name = "Questionnaire"
        verbose_name_plural = "Questionnaires"

    @property
    def file(self):
        """
        If there is a manually uplodaed file it will take precedence.
        """
        if bool(self.uploaded_file):
            return self.uploaded_file
        return self.generated_file

    @property
    def url(self):
        return reverse('questionnaire-detail', args=[self.id])

    @property
    def file_url(self):
        return reverse('send-questionnaire-file', args=[self.id])

    @property
    def site_url(self):
        return "https://" + Site.objects.all()[0].domain + "/"

    @property
    def basename(self):
        """
        Name of file, without path.
        """
        return os.path.basename(self.file.name)

    @property
    def downloadname(self):
        """
        Name of file, without path.
        """
        return self.basename

    @property
    def title_display(self):
        return f"Questionnaire n°{self.numbering} - {self.title}"

    @property
    def sent_date_display(self):
        if not self.sent_date:
            return None
        return self.sent_date.strftime("%A %d %B %Y")

    @property
    def end_date_display(self):
        if not self.end_date:
            return None
        return self.end_date.strftime("%A %d %B %Y")

    @property
    def description_rich_text(self):
        return self.to_rich_text(self.description)

    @property
    def is_published(self):
        return not self.is_draft

    @property
    def has_replies(self):
        for theme in self.themes.all():
            for question in theme.questions.all():
                if len(question.response_files.all()) > 0:
                    return True
        return False

    def __str__(self):
        display_text = f'[ID{self.id}]'
        if self.control:
            display_text += f' [C{self.control.id}]'
        display_text += f' [Q{self.numbering}]'
        display_text += f' - {self.title}'
        return display_text

class QuestionnaireFile(OrderedModel, FileInfoMixin):
    questionnaire = models.ForeignKey(
        to='Questionnaire', verbose_name='questionnaire', related_name='questionnaire_files',
        on_delete=models.CASCADE)
    file = models.FileField(verbose_name="fichier", upload_to=questionnaire_pj_file_path)
    order_with_respect_to = 'questionnaire'

    class Meta:
        ordering = ('questionnaire', 'order')
        verbose_name = 'Questionnaire: Fichier Annexe'
        verbose_name_plural = 'Questionnaire: Fichiers Annexes'

    @property
    def url(self):
        return reverse('send-questionnaire-pj-file', args=[self.id])

    @property
    def basename(self):
        """
        Name of file, without path.
        """
        return os.path.basename(self.file.name)

    @property
    def downloadname(self):
        """
        Name of file, without path.
        """
        return self.basename


class Theme(OrderedModel, WithNumberingMixin):
    title = models.CharField("titre", max_length=255)
    questionnaire = models.ForeignKey(
        to='Questionnaire', verbose_name='questionnaire', related_name='themes',
        null=True, blank=True, on_delete=models.CASCADE)
    order_with_respect_to = 'questionnaire'

    class Meta:
        ordering = ('questionnaire', 'order')
        verbose_name = "Thème"
        verbose_name_plural = "Thèmes"

    @property
    def control(self):
        if not self.questionnaire:
            return None
        return self.questionnaire.control

    def __str__(self):
        display_text = f'[ID{self.id}]'
        if self.control:
            display_text += f' [C{self.control.id}]'
        if self.questionnaire:
            display_text += f' [Q{self.questionnaire.numbering}]'
        display_text += f' [T{self.numbering}]'
        display_text += f' - {self.title}'
        return display_text


class Question(OrderedModel, WithNumberingMixin, DocxMixin):
    description = models.TextField("description")
    theme = models.ForeignKey(
        'theme', verbose_name='thème', related_name='questions',
        null=True, blank=True, on_delete=models.CASCADE)
    order_with_respect_to = 'theme'

    class Meta:
        ordering = ('theme', 'order')
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    @property
    def control(self):
        if not self.theme:
            return None
        return self.theme.control

    @property
    def questionnaire(self):
        if not self.theme:
            return None
        return self.theme.questionnaire

    @property
    def description_rich_text(self):
        return self.to_rich_text(self.description)

    def __str__(self):
        display_text = f'[ID{self.id}] [Num{self.numbering}]'
        if self.control:
            display_text += f' [C{self.control.id}]'
        if self.questionnaire:
            display_text += f' [Q{self.theme.questionnaire.numbering}]'
        if self.theme:
            display_text += f' [T{self.theme.numbering}]'
        display_text += f' - {self.description}'
        return display_text


class QuestionFile(OrderedModel, FileInfoMixin):
    question = models.ForeignKey(
        to='Question', verbose_name='question', related_name='question_files',
        on_delete=models.CASCADE)
    file = models.FileField(verbose_name="fichier", upload_to=question_file_path)
    order_with_respect_to = 'question'

    class Meta:
        ordering = ('question', 'order')
        verbose_name = 'Question: Fichier Annexe'
        verbose_name_plural = 'Question: Fichiers Annexes'

    @property
    def url(self):
        return reverse('send-question-file', args=[self.id])

    @property
    def basename(self):
        """
        Name of file, without path.
        """
        return os.path.basename(self.file.name)

    @property
    def downloadname(self):
        """
        Name of file, without path.
        """
        return self.basename


@cleanup.ignore
class ResponseFile(TimeStampedModel, FileInfoMixin):
    question = models.ForeignKey(
        to='Question', verbose_name='question', related_name='response_files',
        on_delete=models.CASCADE)
    file = models.FileField(verbose_name="fichier", upload_to=response_file_path, max_length=2000)
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, related_name='response_files', on_delete=models.PROTECT)
    is_deleted = models.BooleanField(
        verbose_name="Supprimé", default=False,
        help_text="Ce fichier est-il dans la corbeille ?")

    class Meta:
        verbose_name = 'Réponse: Fichier Déposé'
        verbose_name_plural = 'Réponse: Fichiers Déposés'

    @property
    def url(self):
        return reverse('send-response-file', args=[self.id])

    @property
    def basename(self):
        """
        Name of file, without path and without name prefix.
        """
        prefixer = Prefixer(self)
        if self.is_deleted:
            return prefixer.strip_deleted_file_prefix()
        return prefixer.strip_file_prefix()

    @property
    def downloadname(self):
        """
        Name of file for download, prefixed.
        """
        prefixer = Prefixer(self)
        if self.is_deleted:
            filename = prefixer.strip_deleted_file_prefix()
            return f"{prefixer.make_deleted_file_prefix()}-{filename}"
        filename = prefixer.strip_file_prefix()
        return f"{prefixer.make_file_prefix()}-{filename}"
