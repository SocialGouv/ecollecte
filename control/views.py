import magic
import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponseBadRequest, Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import DetailView, CreateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q

from django.http import HttpResponse
from django.http import FileResponse
import mimetypes
from actstream import action
from actstream.models import model_stream
import json

from .docx import generate_questionnaire_file
from .export_response_files import generate_response_file_list_in_xlsx
from .models import Control, Questionnaire, QuestionFile, QuestionnaireFile, ResponseFile, Question
from .serializers import ControlDetailUserSerializer, ControlSerializerWithoutDraft
from .serializers import ControlSerializer, ControlDetailControlSerializer



class WithListOfControlsMixin(object):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Questionnaires are grouped by control:
        # we get the list of questionnaire from the list of controls
        user_access = self.request.user.profile.access.filter(control__is_deleted=False).all()
        control_list = Control.objects.filter(access__in=user_access).order_by('-id')
        context['controls'] = control_list
        return context


class ControlDetail(LoginRequiredMixin, WithListOfControlsMixin, TemplateView):
    template_name = "ecc/control_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        control_list = context['controls']
        controls_serialized = []
        for control in control_list:
            control_serialized = ControlDetailControlSerializer(instance=control).data
            controls_serialized.append(control_serialized)
        context['controls_json'] = json.dumps(controls_serialized)
        user_serialized = ControlDetailUserSerializer(instance=self.request.user).data
        user_serialized['is_inspector'] = self.request.user.profile.is_inspector
        context['user_json'] = json.dumps(user_serialized)
        return context


class Trash(LoginRequiredMixin, WithListOfControlsMixin, DetailView):
    model = Questionnaire
    template_name = "ecc/trash.html"

    def get_queryset(self):
        user_controls = Control.objects.filter(access__in=self.request.user.profile.access.all())
        queryset = Questionnaire.objects.filter(control__in=user_controls)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response_files = ResponseFile.objects \
            .filter(question__theme__questionnaire=self.get_object()) \
            .filter(is_deleted=True)

        response_file_ids = response_files.values_list('id', flat=True)

        stream = model_stream(ResponseFile)\
            .filter(verb='trashed response-file')\
            .filter(target_object_id__in=list(response_file_ids)) \
            .order_by('timestamp')

        response_file_list = []
        for act in stream:
            response_file = response_files.get(id=act.target_object_id)
            response_file.deletion_date = act.timestamp
            response_file.deletion_user = User.objects.get(id=act.actor_object_id)
            response_file.question_number = str(response_file.question.theme.numbering) + \
                '.' + str(response_file.question.numbering)
            response_file_list.append(response_file)
        response_file_list.sort(key=lambda x: x.question_number)
        context['response_file_list'] = response_file_list

        return context


class QuestionnaireDetail(LoginRequiredMixin, WithListOfControlsMixin, DetailView):
    template_name = "ecc/questionnaire_detail.html"
    context_object_name = 'questionnaire'

    def get(self, request, *args, **kwargs):
        # Before accessing the questionnaire, we log who's accessing it.
        self.add_access_log_entry()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user_controls = Control.objects.filter(access__in=self.request.user.profile.access.all())
        controls_questionnaires = Questionnaire.objects.filter(control__in=user_controls)
        user_questionnaires = []
        for result in controls_questionnaires:
            if not (result.is_draft & self.request.user.profile.access.filter(Q(control=result.control) & Q(access_type='repondant')).exists()):
                user_questionnaires.append(result.id)
        queryset = Questionnaire.objects.filter(id__in=user_questionnaires)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        serializer = ControlSerializerWithoutDraft
        questionnaire = context['object']
        if self.request.user.profile.access.filter(Q(control=questionnaire.control) & Q(access_type='demandeur')).exists():
            serializer = ControlSerializer
        control_list = context['controls']
        controls_serialized = []
        for control in control_list:
            control_serialized = serializer(instance=control).data
            controls_serialized.append(control_serialized)
        context['controls_json'] = json.dumps(controls_serialized)

        return context

    def add_access_log_entry(self):
        questionnaire = self.get_object()
        action_details = {
            'sender': self.request.user,
            'verb': 'accessed questionnaire',
            'target': questionnaire,
        }
        action.send(**action_details)


class QuestionnaireEdit(LoginRequiredMixin, WithListOfControlsMixin, DetailView):
    template_name = "ecc/questionnaire_create.html"
    context_object_name = 'questionnaire'

    def get_queryset(self):
        questionnaire = Questionnaire.objects.filter(id=self.kwargs['pk']).first()
        if not self.request.user.profile.access.filter(Q(control=questionnaire.control) & Q(access_type='demandeur')).exists():
            return Control.objects.none()
        user_controls = Control.objects.filter(access__in=self.request.user.profile.access.all())
        questionnaires = Questionnaire.objects.filter(
            control__in=user_controls,
            editor=self.request.user
        )
        return questionnaires

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        control_list = context['controls']
        controls_serialized = []
        for control in control_list:
            control_serialized = ControlDetailControlSerializer(instance=control).data
            controls_serialized.append(control_serialized)
        context['controls_json'] = json.dumps(controls_serialized)
        user_serialized = ControlDetailUserSerializer(instance=self.request.user).data
        user_serialized['is_inspector'] = self.request.user.profile.is_inspector
        context['user_json'] = json.dumps(user_serialized)
        return context

class QuestionnaireCreate(LoginRequiredMixin, WithListOfControlsMixin, DetailView):
    """
    Creates a questionnaire on a given control (pk of control passed in URL).
    """
    template_name = "ecc/questionnaire_create.html"
    context_object_name = 'control'

    def get_queryset(self):

        user_access = self.request.user.profile.access.filter(access_type='demandeur').all()
        return Control.objects.filter(access__in=user_access)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        control_list = context['controls']
        controls_serialized = []
        for control in control_list:
            control_serialized = ControlDetailControlSerializer(instance=control).data
            controls_serialized.append(control_serialized)
        context['controls_json'] = json.dumps(controls_serialized)
        user_serialized = ControlDetailUserSerializer(instance=self.request.user).data
        user_serialized['is_inspector'] = self.request.user.profile.is_inspector
        context['user_json'] = json.dumps(user_serialized)
        return context
    
class UploadResponseFile(LoginRequiredMixin, CreateView):
    model = ResponseFile
    fields = ('file',)

    def add_upload_action_log(self):
        action_details = {
            'sender': self.request.user,
            'verb': 'uploaded response-file',
            'action_object': self.object,
            'target': self.object.question,
        }
        action.send(**action_details)

    def add_invalid_extension_log(self, invalid_extension):
        action_details = {
            'sender': self.request.user,
            'verb': 'uploaded invalid response-file extension',
            'target': self.object.question,
            'description': f'Detected invalid file extension: "{invalid_extension}"'
            }
        action.send(**action_details)

    def add_invalid_mime_type_log(self, invalid_mime_type):
        action_details = {
            'sender': self.request.user,
            'verb': 'uploaded invalid response-file',
            'target': self.object.question,
            'description': f'Detected invalid response-file mime type: "{invalid_mime_type}"'
            }
        action.send(**action_details)

    def file_extension_is_valid(self, extension):
        
        split_extensions = extension.split(".")
        if len(split_extensions) > 2: 
            return False
        normalized_extension = f".{split_extensions[-1].lower()}"
        return normalized_extension not in settings.UPLOAD_FILE_EXTENSION_BLACKLIST

    def file_mime_type_is_valid(self, mime_type):
        blacklist = settings.UPLOAD_FILE_MIME_TYPE_BLACKLIST
        if any(match.lower() in mime_type.lower() for match in blacklist):
            return False
        return True

    def form_valid(self, form):
        
        if isinstance(self.request.FILES.getlist('file'), list) and len(self.request.FILES.getlist('file')) > 1:
            return HttpResponseForbidden(
            "Le téléchargement de plusieurs fichiers via un seul champ est interdit."
        )
            
        if (
            "x-infection-found" in [header.lower() for header in self.request.headers]
            or "x-virus-name" in [header.lower() for header in self.request.headers]
        ):
            return HttpResponseForbidden(
                "Ce fichier a été notifié comme contenant un virus, merci de vérifier"
                " celui-ci avant de le déposer à nouveau."
            )
        try:
            question_id = form.data['question_id']
        except KeyError:
            return HttpResponseBadRequest("Question ID was missing on file upload")
        question = Question.objects.get(pk=question_id)
        control = question.theme.questionnaire.control
        if control.is_deleted:
            return HttpResponseForbidden("Control is deleted.")
        if not self.request.user.profile.access.filter(Q(control=control) & Q(access_type='repondant')).exists():
            return HttpResponseForbidden("User is not authorized to access this ressource")
        get_object_or_404(
            Question,
            pk=question_id,
            theme__questionnaire__in=self.request.user.profile.questionnaires
        )
        self.object = form.save(commit=False)
        self.object.question_id = question_id
        self.object.author = self.request.user
        file_object = self.object.file
        file_extension = os.path.splitext(file_object.name)[1]

        if not self.file_extension_is_valid(file_extension):
            self.add_invalid_extension_log(file_extension)
            return HttpResponseForbidden(
                f"Cette extension de fichier n'est pas autorisée : {file_extension}"
            )

        mime_type = magic.from_buffer(file_object.read(2048), mime=True)
        if not self.file_mime_type_is_valid(mime_type):
            self.add_invalid_mime_type_log(mime_type)
            return HttpResponseForbidden(
                f"Ce type de fichier n'est pas autorisé: {mime_type}"
            )

        if len(file_object.name) > settings.MAX_FILENAME_LENGTH:
            extension_length = len(file_extension)
            max_length = settings.MAX_FILENAME_LENGTH - extension_length
            self.object.file.name = f"{file_object.name[:max_length]}{file_extension}"

        MAX_SIZE_BYTES = 1048576 * settings.UPLOAD_FILE_MAX_SIZE_MB
        if file_object.file.size > MAX_SIZE_BYTES:
            return HttpResponseForbidden(
                f"La taille du fichier dépasse la limite autorisée "
                f"de {settings.UPLOAD_FILE_MAX_SIZE_MB}Mo."
            )
        self.object.save()
        self.add_upload_action_log()
        data = {'status': 'success'}
        response = JsonResponse(data)
        return response

    def format_form_errors(self, form):
        error_message = ""
        for field in form.errors:
            error_message += form.errors[field]
        return error_message

    def form_invalid(self, form):
        data = {
            'status': 'error',
            'error': self.format_form_errors(form),
        }
        response = JsonResponse(data, status=400)
        return response


class SendFileMixin(SingleObjectMixin):
    """
    Inheriting classes should override :
    - model to specify the data type of the file. The model class should implement
      a downloadname property.
    - (optional) get_queryset() to restrict the accessible files.
    """
    model = None
    file_type = None

    # used in a View, this function overrides the View's GET request handler.
    def get(self, request, *args, **kwargs):
        # get the object fetched by SingleObjectMixin
        obj = self.get_object()
        self.add_access_log_entry(accessed_object=obj)
        
        content_type, encoding = mimetypes.guess_type(obj.file.path)
        content_type = content_type or 'application/octet-stream'

        with open(obj.file.path, 'rb') as f:
            file_data = f.read()

        response = HttpResponse(file_data, content_type=content_type)
        
        filename = os.path.basename(obj.file.path)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    def add_access_log_entry(self, accessed_object):
        verb = f'accessed {self.file_type}'
        if self.file_type == 'response-file' and accessed_object.is_deleted:
            verb = 'accessed trashed-response-file'
        action_details = {
            'sender': self.request.user,
            'verb': verb,
            'target': accessed_object,
        }
        action.send(**action_details)


class SendQuestionnaireFile(SendFileMixin, LoginRequiredMixin, View):
    model = Questionnaire
    file_type = 'questionnaire-file'

    def get(self, request, *args, **kwargs):
        """
        Before sending the questionnaire file, we generate it.
        This means that the file is geneated every time this view is called - tipically
        when the user downloads the file.
        """
        questionnaire = self.get_object()
        if questionnaire.is_draft:
            if not questionnaire.control in request.user.profile.user_controls("demandeur"):
                raise Http404
        generate_questionnaire_file(questionnaire)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Questionnaire.objects.filter(
            control__in=Control.objects.filter(access__in=self.request.user.profile.access.all()))


class SendQuestionFile(SendFileMixin, LoginRequiredMixin, View):
    model = QuestionFile
    file_type = 'question-file'

    def get_queryset(self):
        # The user should only have access to files that belong to the control
        # he was associated with. That's why we filter-out based on the user's
        # control.
        user_controls = Control.objects.filter(access__in=self.request.user.profile.access.all())
        return self.model.objects.filter(
            question__theme__questionnaire__control__in=user_controls)

class SendQuestionnairePjFile(SendFileMixin, LoginRequiredMixin, View):
    model = QuestionnaireFile
    file_type = 'questionnaire-file'

    def get_queryset(self):
        # The user should only have access to files that belong to the control
        # he was associated with. That's why we filter-out based on the user's
        # control.
        user_controls = Control.objects.filter(access__in=self.request.user.profile.access.all())
        return self.model.objects.filter(
            questionnaire__control__in=user_controls)



class SendResponseFile(SendQuestionFile):
    model = ResponseFile
    file_type = 'response-file'


class SendResponseFileList(SingleObjectMixin, LoginRequiredMixin, View):
    model = Questionnaire

    def get_queryset(self):
        user_controls = Control.objects.filter(access__in=self.request.user.profile.access.all())
        queryset = Questionnaire.objects.filter(control__in=user_controls)
        queryset = queryset.filter(is_draft=False)
        return queryset

    def get(self, request, *args, **kwargs):
        questionnaire = self.get_object()
        try:
            file = generate_response_file_list_in_xlsx(questionnaire)
            self.add_log_entry(verb='exported responses in xls', questionnaire=questionnaire)
            response = FileResponse(open(file.name, 'rb'), as_attachment=True,
                                    filename=f'réponses_questionnaire_{questionnaire.numbering}.xlsx')
            return response
        except Exception as e:
            self.add_log_entry(
                verb='exported responses in xls - fail', questionnaire=questionnaire, description=str(e)
            )
        finally:
            os.remove(file.name)

    def add_log_entry(self, verb, questionnaire, description=""):
        action_details = {
            'description': description,
            'sender': self.request.user,
            'verb': verb,
            'action_object': questionnaire.control,
            'target': questionnaire
        }

        action.send(**action_details)
