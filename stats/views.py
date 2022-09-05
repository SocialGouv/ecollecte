from datetime import datetime, timedelta, timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import TemplateView

from actstream.models import Action


ACTION_CREATED_CONTROL = "created control"
ACTION_PUBLISHED_QUESTIONNAIRE = "published questionnaire"
ACTION_PUBLISHED_QUESTION = "published question"
ACTION_UPLOADED_RESPONSE = "uploaded response-file"
ACTION_LOGGED_IN = "logged in"


class Stats(LoginRequiredMixin, TemplateView):
    template_name = "stats/stats.html"

    def complete_datas(self, datas):
        """
        Remplissage des mois manquants pour affichage clair des statistiques.
        """
        year = datetime.today().year
        month = datetime.today().month
        for m in range(1, 13):
            if m > month:
                year_to_use = year - 1
            else:
                year_to_use = year
            month_date = datetime(year=year_to_use, month=m, day=1, tzinfo=timezone(timedelta(hours=2)))
            for data in datas:
                if data[0] == month_date:
                    break
            else:
                datas[(11 - month + m) % 12][0] = datetime(year=year_to_use, month=m, day=1)

        return datas


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = datetime.today().month

        controls = [[0, 0] for i in range(12)]
        actions = Action.objects.filter(verb=ACTION_CREATED_CONTROL).all()
        dates = actions.datetimes("timestamp", kind="month")
        for date in dates:
            controls[(11 - month + date.month) % 12] = [
                date,
                actions.filter(timestamp__month=date.month).count(),
            ]
        context["controls"] = self.complete_datas(controls)

        questionnaires = [[0, 0] for i in range(12)]
        actions = Action.objects.filter(verb=ACTION_PUBLISHED_QUESTIONNAIRE).all()
        dates = actions.datetimes("timestamp", kind="month")
        for date in dates:
            questionnaires[(11 - month + date.month) % 12] = [
                date,
                actions.filter(timestamp__month=date.month).count(),
            ]
        context["questionnaires"] = self.complete_datas(questionnaires)

        questions = [[0, 0] for i in range(12)]
        actions = Action.objects.filter(verb=ACTION_PUBLISHED_QUESTION).all()
        dates = actions.datetimes("timestamp", kind="month")
        for date in dates:
            questions[(11 - month + date.month) % 12] = [
                date,
                actions.filter(timestamp__month=date.month).count(),
            ]
        context["questions"] = self.complete_datas(questions)

        users = [[0, 0] for i in range(12)]
        all_users = User.objects.all()
        dates = all_users.datetimes("date_joined", kind="month")
        for date in dates:
            users[(11 - month + date.month) % 12] = [
                date,
                all_users.filter(date_joined__month=date.month).count()
            ]
        context["users"] = self.complete_datas(users)

        responses = [[0, 0, 0] for i in range(12)]
        actions = Action.objects.filter(verb=ACTION_UPLOADED_RESPONSE).all()
        dates = actions.datetimes("timestamp", kind="month")
        for date in dates:
            month_size = 0
            for fil in actions.filter(timestamp__month=date.month).all():
                try:
                    month_size += fil.action_object.file.size
                except:
                    pass
            responses[(11 - month + date.month) % 12] = [
                date,
                actions.filter(timestamp__month=date.month).count(),
                month_size,
            ]
        context["responses"] = self.complete_datas(responses)

        connections = [[0, 0] for i in range(12)]
        actions = Action.objects.filter(verb=ACTION_LOGGED_IN).all()
        dates = actions.datetimes("timestamp", kind="month")
        for date in dates:
            connections[(11 - month + date.month) % 12] = [
                date,
                actions.filter(timestamp__month=date.month).count(),
            ]
        context["connections"] = self.complete_datas(connections)

        return context
