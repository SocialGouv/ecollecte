# Generated by Django 2.2.7 on 2019-11-21 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faq', '0004_faqitem_add_default_data'),
    ]

    operations = [
        migrations.RunSQL("update faq_faqitem set description = 'Il se peut que vous n''ayez pas d''éléments de réponse de de pièces justificatives à apporter à une question. Dans ce cas, nous vous recommandons :<ul><li>De créer un document, par exemple un fichier Word, où vous expliquerez brièvement que vous n''avez pas d''élément de réponse.</li><li>Ensuite, vous pourrez déposer ce fichier Word ou une version PDF sous la question concernée.</li></ul></br>Cette information est importante pour les équipes d''instruction. Elle évitera les malentendus et le risque que la même question vous soit reposée dans un prochain questionnaire.' where slug = 'question1_default';"),
        migrations.RunSQL("update faq_faqitem set description = 'Non. Il n''est pas possible de supprimer ou remplacer un document déposé sur «ecollecte». En revanche, vous pouvez informer l''équipe d''instruction par email ou par téléphone.' where slug = 'question4_default';"),
    ]