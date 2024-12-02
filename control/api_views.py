from functools import partial

import django.dispatch
from control.serializers import ControlSerializer, ControlListSerializer
from django.http import HttpResponse
from django.db import connection
from actstream import action
from django.core.files import File
from django.db.models import Q
from rest_framework import (decorators, generics, mixins, serializers, status,
                            viewsets)
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from control.permissions import (ControlIsNotDeleted, OnlyRepondantCanAccess,
                                 OnlyInspectorCanCreate, OnlyAuthenticatedCanAccess,
                                 OnlyEditorCanChangeQuestionnaire,
                                 ControlDemandeurAccess, QuestionnaireIsDraft)
from user_profiles.models import Access
from user_profiles.serializers import AccessSerializer, UserProfileSerializer

from . import serializers as control_serializers
from .models import (Control, Question, QuestionFile, Questionnaire, QuestionnaireFile,
                     ResponseFile, Theme)

# This signal is triggered after the questionnaire is created via the API
questionnaire_api_post_save = django.dispatch.Signal()
# This signal is triggered after the questionnaire is saved via the API
questionnaire_api_post_update = django.dispatch.Signal()


class ControlViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    permission_classes_by_action = {
        "create": (OnlyInspectorCanCreate,),
        "update": (ControlDemandeurAccess,),
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes_by_action["update"]]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["profile"] = self.request.user.profile
        return context

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return control_serializers.ControlUpdateSerializer
        return control_serializers.ControlFilteredSerializer

    def get_queryset(self):
        if not self.request.user.is_anonymous:
            return Control.objects.filter(Q(access__in=self.request.user.profile.access.all()) & Q(is_deleted=False))

    def add_log_entry(self, control, verb):
        action_details = {
            'sender': self.request.user,
            'verb': verb,
            'action_object': control
        }
        action.send(**action_details)
        
    def add_log_duplicate_entry(self, controlSource, controlDestination, verb):
        action_details = {
            'sender': self.request.user,
            'verb': verb,
            'action_object': controlDestination,
            'target': controlSource
        }
        action.send(**action_details)

    def create(self, request, *args, **kwargs):
        response = super(ControlViewSet, self).create(request, *args, **kwargs)
        control = Control.objects.active().get(id=response.data['id'])
        access_type = 'demandeur'
        profile = request.user.profile
        # The current user is automatically added to the created control
        Access.objects.create(access_type=access_type, userprofile=profile, control=control)
        if request.data.__contains__('idCtlSource') :
            print ("Duplication : ", request.data['idCtlSource'])
            controlSource = Control.objects.active().get(id=request.data['idCtlSource'])
            self.add_log_duplicate_entry( controlSource=controlSource, controlDestination=control, verb='created control')
        else:
            print ("Creation")
            self.add_log_entry(control=control, verb='created control')
  
        return response
    
    def update(self, request, *args, **kwargs):
        response = super(ControlViewSet, self).update(request, *args, **kwargs)
        control = self.get_queryset().get(id=response.data['id'])
        self.add_log_entry(control=control, verb='updated control')
        print ("update control")
        return response

    
    @decorators.action(detail=True, methods=['get'], url_path='quest_themes')
    def quest_themes(self, request, pk):
        quest_themes_list = Control.objects.filter(id=pk)
        ctl_Serializer = ControlSerializer(quest_themes_list, many=True)
        return Response(ctl_Serializer.data)
    
    @decorators.action(detail=False, methods=['get'], url_path='controls_list')
    def controls_list(self, request):
        ctl_list = Control.objects.filter(Q(access__in=self.request.user.profile.access.all()) & Q(is_deleted=False))
        ctl_Serializer = ControlListSerializer(ctl_list, many=True)
        return Response(ctl_Serializer.data)
    
    @decorators.action(detail=True, methods=['get'], url_path='users')
    def users(self, request, pk):
        users = []
        for acc in self.get_object().access.all():
            users.append(acc.userprofile)
        serialized_users = UserProfileSerializer(list(set(users)), many=True)
        return Response(serialized_users.data)

    @decorators.action(detail=True, methods=['get'], url_path='audited')
    def audited(self, request, pk):
        users = []
        for acc in self.get_object().access.all():
            if acc.access_type == 'repondant':
                users.append(acc.userprofile)
        serialized_users = UserProfileSerializer(list(set(users)), many=True)
        return Response(serialized_users.data)

    @decorators.action(detail=True, methods=['get'], url_path='inspectors')
    def inspectors(self, request, pk):
        users = []
        for acc in self.get_object().access.all():
            if acc.access_type == 'demandeur':
                users.append(acc.userprofile)
        serialized_users = UserProfileSerializer(list(set(users)), many=True)
        return Response(serialized_users.data)


    @decorators.action(detail=True, methods=['get'], url_path='depositors')
    def depositors(self, request, pk):
        users = []
        for questionnaire in self.get_object().questionnaires.all():
            for theme in questionnaire.themes.all():
                for question in theme.questions.all():
                    for response_file in question.response_files.all():
                        users.append(response_file.author.profile)
        serialized_users = UserProfileSerializer(list(set(users)), many=True)
        return Response(serialized_users.data)
    
    @decorators.action(detail=True, methods=['get'], url_path='access')
    def access(self, request, pk):
        serialized_access = AccessSerializer(self.get_object().access.filter(Q(userprofile=request.user.profile) & Q(control__is_deleted=False)).all(), many=True)
        return Response(serialized_access.data)

    @decorators.action(detail=True, methods=['get'], url_path='unique-code')
    def check_unique_code(self, request, pk):
        isCodeExist = Control.objects.filter(reference_code=request.query_params.get('code')).exists()
        return HttpResponse(isCodeExist)


class QuestionViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = control_serializers.QuestionSerializer

    def get_queryset(self):
        queryset = Question.objects.filter(
            theme__questionnaire__in=self.request.user.profile.questionnaires)
        return queryset


class QuestionFileViewSet(mixins.DestroyModelMixin,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = control_serializers.QuestionFileSerializer
    parser_classes = (MultiPartParser, FormParser)
    filterset_fields = ('question',)
    permission_classes = (ControlDemandeurAccess, ControlIsNotDeleted, QuestionnaireIsDraft)

    def get_queryset(self):
        queryset = QuestionFile.objects.filter(
            Q(question__theme__questionnaire__control__is_deleted=False) &
            Q(question__theme__questionnaire__in=self.request.user.profile.questionnaires)
        )
        return queryset

    def perform_create(self, serializer):
        question = serializer.validated_data['question']
        # Before creating the QuestionFile, let's check that permission are ok for
        # the associated Question object.
        self.check_object_permissions(self.request, question)
        serializer.save(file=self.request.data.get('file'))

class QuestionnaireFileViewSet(mixins.DestroyModelMixin,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = control_serializers.QuestionnaireFileSerializer
    parser_classes = (MultiPartParser, FormParser)
    filterset_fields = ('questionnaire',)
    permission_classes = (ControlDemandeurAccess, ControlIsNotDeleted, QuestionnaireIsDraft)

    def get_queryset(self):
        queryset = QuestionnaireFile.objects.filter(
            questionnaire__in=self.request.user.profile.questionnaires)
        return queryset

    def perform_create(self, serializer):
        questionnaire = serializer.validated_data['questionnaire']
        # Before creating the QuestionFile, let's check that permission are ok for
        # the associated Question object.
        self.check_object_permissions(self.request, questionnaire)
        serializer.save(file=self.request.data.get('file'))


class ResponseFileTrash(mixins.UpdateModelMixin, generics.GenericAPIView):
    serializer_class = control_serializers.ResponseFileTrashSerializer
    permission_classes = (OnlyRepondantCanAccess,)

    def get_queryset(self):
        queryset = ResponseFile.objects.filter(
            question__theme__questionnaire__control__in=Control.objects.filter(access__in=self.request.user.profile.access.all())) # Modifier par les controls des access
        return queryset

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = self.get_object()

        if not serializer.validated_data['is_deleted']:
            # un-trash : not implemented yet
            raise serializers.ValidationError('Vous ne pouvez sortir un fichier réponse de la corbeille.')

        if instance.is_deleted:
            raise serializers.ValidationError('Vous ne pouvez mettre à la corbeille un fichier qui y est déja.')

        # Save a new file, that gets uploaded to the deleted files path.
        deleted_file = File(instance.file, name=instance.basename)
        serializer.save(file=deleted_file)

        # Log deletion action
        if serializer.validated_data['is_deleted']:
            action_details = {
                'sender': self.request.user,
                'verb': 'trashed response-file',
                'target': instance,
            }
            action.send(**action_details)

        # Delete file left at old path
        instance.file.delete(False)


class ThemeViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = control_serializers.ThemeSerializer
    permission_classes = (ControlDemandeurAccess, QuestionnaireIsDraft)

    def get_queryset(self):
        questionnaires = Questionnaire.objects.filter(
            control__in=Control.objects.filter(access__in=self.request.user.profile.access.all()))
        queryset = Theme.objects.filter(questionnaire__in=questionnaires)
        return queryset


class QuestionnaireViewSet(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = control_serializers.QuestionnaireSerializer
    permission_classes_by_action = {
        "create": (ControlDemandeurAccess, OnlyEditorCanChangeQuestionnaire, QuestionnaireIsDraft),
        "update": (OnlyAuthenticatedCanAccess, ControlIsNotDeleted),
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes_by_action["create"]]

    def get_queryset(self):
        try:
            questionnaire = Questionnaire.objects.get(pk=self.request.data.get("id"))
            control = questionnaire.control
        except Exception:
            control = Control.objects.get(pk=self.request.data.get("control"))
        queryset = Questionnaire.objects.filter(
            control__in=Control.objects.filter(access__in=self.request.user.profile.access.all()))
        if not self.request.user.profile.access.filter(Q(control=control) & Q(access_type='demandeur')).exists():
            queryset = queryset.filter(is_draft=False)
        return queryset

    

    def __create_or_update(self, request, save_questionnaire_func, is_update):
        if is_update:
            pre_existing_qr = self.get_object()  # throws 404 if no qr
            control = pre_existing_qr.control
            verb = "updated"
            if pre_existing_qr.is_draft is True:
                # Only Inspector can publish a Questionnaire
                if request.data.get("is_draft") is False:
                    if not request.user.profile.access.filter(Q(control=control) & Q(access_type='demandeur')).exists():
                        e = PermissionDenied(
                            detail=(
                                "Only inspectors can publish questionnaires "
                                "in active controls that they belong to."),
                            code=status.HTTP_403_FORBIDDEN
                        )
                        raise e
                    verb = "published"
                else:
                    # Only Editor can change a Questionnaire
                    if not request.user.profile.access.filter(Q(control=control) & Q(access_type='demandeur')).exists():
                        e = PermissionDenied(
                            detail=(
                                "Only editors can edit questionnaires "
                                "in active controls that they belong to."),
                            code=status.HTTP_403_FORBIDDEN
                        )
                        raise e
                    if not pre_existing_qr.editor or pre_existing_qr.editor != request.user:
                        e = PermissionDenied(
                            detail=(
                                "Only inspectors can edit questionnaires "
                                "in active controls that they belong to."),
                            code=status.HTTP_403_FORBIDDEN
                        )
                        raise e
            else:
                # Only Audited can answer a Questionnaire when published
                if (
                    pre_existing_qr.is_replied is False
                    and request.data.get("is_replied") is True
                ):
                    if not request.user.profile.access.filter(Q(control=control) & Q(access_type='repondant')).exists():
                        e = PermissionDenied(
                            detail=("Only auditeds can answer questionnaires."),
                            code=status.HTTP_403_FORBIDDEN
                        )
                        raise e
                # Only Inspectors can finalize a Questionnaire Replied
                elif (
                    pre_existing_qr.is_replied is True
                    and pre_existing_qr.is_finalized is False
                    and request.data.get("is_finalized") is True
                ):
                    if not request.user.profile.access.filter(Q(control=control) & Q(access_type='demandeur')).exists():
                        e = PermissionDenied(
                            detail=(
                                "Only inspectors can finalize questionnaires "
                                "in active controls that they belong to."
                            ),
                            code=status.HTTP_403_FORBIDDEN
                        )
                        raise e
                # Only Inspectors can change a published Questionnaire response date
                elif (
                    pre_existing_qr.is_draft is False
                    and pre_existing_qr.end_date != request.data.get("end_date")
                ):
                    if not request.user.profile.access.filter(Q(control=control) & Q(access_type='demandeur')).exists():
                        e = PermissionDenied(
                            detail=(
                                "Only inspectors can change response date "
                                "in active questionnaires that they belong to."
                            ),
                            code=status.HTTP_403_FORBIDDEN
                        )
                        raise e
                # No other modification is possible
                else:
                    e = PermissionDenied(
                        detail="Changing this resource is not allowed.",
                        code=status.HTTP_403_FORBIDDEN
                    )
                    raise e
        else:
            pre_existing_qr = None
            verb = "created"

        def log(saved_object):
            self.__log_action(request.user, verb, saved_object, saved_qr.control)

        validated_themes_and_questions = self.__validate_all(request, verb, pre_existing_qr)
        response = save_questionnaire_func()
        saved_qr = Questionnaire.objects.get(id=response.data['id'])
        saved_qr.editor = request.user
        saved_qr.save()

        log(saved_qr)

        if is_update:
            def log_delete(saved_object):
                self.__log_action(request.user, 'deleted', saved_object, saved_qr.control)

            self.__delete_objects_not_in_request_data(qr_in_db=saved_qr,
                                                      themes_request_data=validated_themes_and_questions,
                                                      log_delete_func=log_delete)

        self.__save_themes_and_questions(qr_in_db=saved_qr,
                                         themes_request_data=validated_themes_and_questions,
                                         log_func=log)

        # Use the read serializer to output the response data.
        response.data = control_serializers.QuestionnaireSerializer(instance=saved_qr).data
        if not is_update:
            questionnaire_api_post_save.send(sender=Questionnaire, instance=saved_qr)
        questionnaire_api_post_update.send(sender=Questionnaire, instance=saved_qr, session_user=self.request.user)
        return response

    def create(self, request, *args, **kwargs):
        save_questionnaire_func = partial(super(QuestionnaireViewSet, self).create, request, *args, **kwargs)

        return self.__create_or_update(request, save_questionnaire_func, is_update=False)

    def update(self, request, *args, **kwargs):
        save_questionnaire_func = partial(super(QuestionnaireViewSet, self).update, request, *args, **kwargs)

        return self.__create_or_update(request, save_questionnaire_func, is_update=True)

    def __validate_all(self, request, verb, questionnaire_in_db=None):
        """
        Validate the themes and questions coming from the request. If it's an update request, we validate that the
        request data is appropriate for updating the questionnaire already in db.
        :param questionnaire_in_db: questionnaire already saved in db.
        :return:
        """
        serializer = control_serializers.QuestionnaireUpdateSerializer(questionnaire_in_db, data=request.data)
        serializer.is_valid(raise_exception=True)

        control = serializer.validated_data['control']
        if verb == "created" and (control is None or control.is_deleted):
            e = PermissionDenied(
                detail=(
                    'Users can only create questionnaires '
                    'in active controls.'
                ),
                code=status.HTTP_403_FORBIDDEN,
            )
            raise e
        if request.user.is_anonymous:
            e = PermissionDenied(
                detail=("Can only create questionnaires when connected."),
                code=status.HTTP_403_FORBIDDEN,
            )
            raise e
        if control is not None and not request.user.profile.access.all().filter(control__id=control.id).exists():
            e = PermissionDenied(
                detail=(
                    'Users can only create questionnaires '
                    'in active controls that they belong to.'),
                code=status.HTTP_403_FORBIDDEN)
            raise e
        if verb == "created" and control is not None and control not in request.user.profile.user_controls('demandeur'):
            e = PermissionDenied(
                detail=(
                    'Users can only create questionnaires '
                    'when they are Demandeur.'),
                code=status.HTTP_403_FORBIDDEN)
            raise e

        return serializer.validated_data.get('themes', [])

    def __delete_objects_not_in_request_data(self, qr_in_db, themes_request_data, log_delete_func):
        """
        This is for an questionnaire update request only.
        This function deletes objects (questions or themes) that are present in the request data, but not in the DB.
        Example :
        The request has : themes: [ {id:1, title:"AAA"}, {id:3, title:"CCC"} ]
        The DB has themes with ids 1, 2 and 3.
        This function will delete theme 2 from DB.

        Note that in request data, themes and questions don't always have an id : objects created in front-end don't
        have an id because they haven't been saved to DB yet.

        :param qr_in_db: questionnaire currently in DB.
        :param themes_request_data: list of themes coming from update request.
        :param function for logging the action of deleting.
        :return:
        """

        def __find_child_theme_by_id(parent_questionnaire, theme_id):
            return self.__find_child_obj_by_id(parent_questionnaire, theme_id, Theme)

        # remove themes from DB if they aren't in request data.
        theme_ids_in_request = [theme_request_data.get('id') for theme_request_data in themes_request_data]
        for theme_in_db in qr_in_db.themes.all():
            if theme_in_db.id not in theme_ids_in_request:
                theme_in_db.delete()
                log_delete_func(theme_in_db)

        for theme_request_data in themes_request_data:
            # Find theme in DB corresponding to theme in request_data.
            theme_in_db = __find_child_theme_by_id(qr_in_db, theme_request_data.get('id'))
            if theme_in_db is None:
                continue

            questions_request_data = theme_request_data.get('questions', [])
            question_ids_in_request = \
                [question_request_data.get('id') for question_request_data in questions_request_data]
            for question_in_db in theme_in_db.questions.all():
                # if question not in request : delete it.
                if question_in_db.id not in question_ids_in_request:
                    question_in_db.delete()
                    log_delete_func(question_in_db)

    def __find_child_obj_by_id(self, parent_obj, child_id, child_class):
        """
        Look through the children of parent_obj, and return a child object with id=child_id. If not found return none.
        :param parent_obj: e.g. an instance of Questionnaire
        :param child_id: e.g. 3 (we are looking for a child with id=3)
        :param child_class: e.g. Theme (the children to look through are of type Theme)
        :return:
        """
        if parent_obj is None or child_id is None:
            return None
        child_class_name_plural = child_class.__name__.lower() + 's'

        children = getattr(parent_obj, child_class_name_plural)
        children_ids = children.all().values_list('id')
        if children_ids.filter(id=child_id).exists():
            return child_class.objects.get(id=child_id)
        return None

    def __save_themes_and_questions(self, qr_in_db, themes_request_data, log_func):
        """
        For create- or update-questionnaire request : save the data from the request in the db.
        If the object in request
        data (theme or question) has an id, we try to find a corresponding existing object in DB and update it.
        Otherwise we will create a new object in DB.
        Example :
        The request has : themes: [ {id:2, title:"AAA"}, {title:"BBB"}, {id:12345, title:"CCC"} ]
        The DB has one theme with id 2.
        This function will update theme 2, create a new theme "BBB", and create a new theme "CCC" (because the id is
        bad, so it is ignored.)
        :param qr_in_db: questionnaire currently saved in DB
        :param themes_request_data: themes coming from the data in the http request
        :param verb: create or update
        :return:
        """

        for theme_request_data in themes_request_data:
            theme_in_db = self.__find_child_obj_by_id(qr_in_db, theme_request_data.get('id'), Theme)
            theme_serializer = control_serializers.ThemeSerializer(theme_in_db, data=theme_request_data)
            theme_serializer.is_valid(raise_exception=True)
            saved_theme = theme_serializer.save(questionnaire=qr_in_db)
            log_func(saved_theme)

            questions_data = theme_request_data.get('questions', [])
            for question_data in questions_data:
                question_in_db = self.__find_child_obj_by_id(
                    saved_theme, question_data.get('id'), Question)
                question_serializer = control_serializers.QuestionUpdateSerializer(
                    question_in_db, data=question_data)
                question_serializer.is_valid(raise_exception=True)
                saved_question = question_serializer.save(theme=saved_theme)
                log_func(saved_question)

    def __log_action(self, user, verb, saved_object, control):
        action_details = {
            'sender': user,
            'verb': verb + ' ' + saved_object.__class__.__name__.lower(),
            'action_object': saved_object,
            'target': control,
        }
        action.send(**action_details)
