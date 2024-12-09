from django.contrib import admin

from control.models import Control, Questionnaire
from logs.actions import add_log_entry


def find_parent_control(obj):
    if isinstance(obj, Control):
        return obj
    if isinstance(obj, Questionnaire):
        return obj.control
    return obj


def soft_delete(modeladmin, request, queryset):
    for item in queryset:
        item.delete()
        parent = find_parent_control(item)
        add_log_entry(verb='admin soft deleted', session_user=request.user, obj=item, target=parent)


def undelete(modeladmin, request, queryset):
    for item in queryset:
        item.restore()
        add_log_entry(verb='admin undeleted', session_user=request.user, obj=item, target=item)


soft_delete.short_description = "Désactiver les objets sélectionnés"
undelete.short_description = "Ré-activer les objets sélectionnés"


class IsActiveFilter(admin.SimpleListFilter):
    title = 'active'
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.filter(deleted_at__isnull=True)
        elif value == 'no':
            return queryset.filter(deleted_at__isnull=False)
        return queryset

class IsModelFilter(admin.SimpleListFilter):
    title = 'modèle'
    parameter_name = 'is_model'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.filter(is_model=True)
        elif value == 'no':
            return queryset.filter(is_model=False)
        return queryset

class SoftDeletedAdmin(object):
    actions = [soft_delete, undelete]

    def is_active(self, instance):
        return not instance.is_deleted
    is_active.boolean = True
    is_active.short_description = "active"

    def get_list_display(self, request):
        return super().get_list_display(request) + ('is_model', 'deleted_at', 'is_active')

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ('is_model', 'is_deleted', 'deleted_at',)

    def has_delete_permission(self, request, obj=None):
        return False
