<template>
  <div>
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">
          <span data-v-d81dfb="" class="number"></span>
          <span class="sr-only">En cours de consultation</span>
          Etape 1 : Renseigner l'introduction
        </h2>
      </div>
      <div class="card-body pb-6">
        <form ref="form">
          <div class="form-group">
            <label class="form-label" id="questionnaireTitle" for="questionnaire_title">
              Quel titre souhaitez vous donner au questionnaire n°{{ questionnaireNumbering }} ?
              <span class="form-required">*</span>
            </label>
            <span class="text-muted" id="questionnaireTitleHelp">
              Exemple :
              <strong>"Présentation générale"</strong>
              ou
              <strong>"Suite à la réunion du ..."</strong>. 255 caractères maximum.
            </span>
            <input id="questionnaire_title"
                   type="text"
                   aria-labelledby="questionnaireTitle"
                   aria-describedby="questionnaireTitleHelp"
                   class="form-control"
                   v-model="title"
                   maxlength="255"
                   required>
          </div>
          <div class="form-group">
            <label class="form-label" id="questionnaireDescription" for="questionnaire_description">
              Vous pouvez modifier le texte d'introduction du questionnaire
              n°{{ questionnaireNumbering }}, si vous le souhaitez :
            </label>
            <textarea id="questionnaire_description"
                      class="form-control"
                      aria-labelledby="questionnaireDescription"
                      placeholder="Si nécessaire, décrivez votre questionnaire ici"
                      rows="6"
                      v-bind:class="{ 'state-invalid': errors.description }"
                      v-model="description">
            </textarea>
            <p class="text-muted pl-2" v-if="errors.description">
              <span class="fa fa-warning" aria-hidden="true"></span> {{ errors.description.join(' / ')}}
            </p>
          </div>
          <div class="form-group">
            <label class="form-label" id="questionnaireEndDate" for="questionnaire_enddate">
              Vous pouvez indiquer la date limite de réponse :
            </label>
            <datepicker id="questionnaire_enddate"
                        class="blue"
                        aria-labelledby="questionnaireEndDate"
                        v-model="end_date"
                        :language="fr"
                        :typeable="true"
                        :use-utc="true"
                        :placeholder="placeholder"
                        :format="format"
                        :monday-first="true">
            </datepicker>
          </div>
          <div class="form-group">
            <questionnaire-file-upload :questionnaire="questionnaire"></questionnaire-file-upload>
            <questionnaire-file-list :files="questionnaire.questionnaire_files" :with-delete="true">
            </questionnaire-file-list>
          </div>
        </form>
        <a class="wizard-step-graphics">
          <span class="sr-only">Étape validée</span>
        </a>
      </div>
    </div>
  </div>
</template>


<script>
import Vue from 'vue'
import Datepicker from 'vuejs-datepicker'
import { mapFields } from 'vuex-map-fields'
import fr from '../utils/vuejs-datepicker-locale-fr'
import reportValidity from 'report-validity'
import QuestionnaireFileUpload from './QuestionnaireFileUpload'
import QuestionnaireFileList from './QuestionnaireFileList'

// eslint-disable-next-line no-multi-str
const DESCRIPTION_DEFAULT = 'À l’occasion de cette procédure, \
nous vous demandons de nous transmettre des renseignements et des justifications \
sur les points énumérés dans ce questionnaire.\nVous voudrez bien nous faire \
parvenir au fur et à mesure votre réponse. \
\nNous restons à votre disposition ainsi qu’à celle de vos \
services pour toute information complémentaire qu’appellerait ce questionnaire.'

const QuestionnaireMetadataCreate = Vue.extend({
  props: {
    questionnaireNumbering: Number,
    questionnaire: Object,
  },
  data() {
    return {
      errors: [],
      fr: fr, // locale for datepicker
      format: "yyyy-MM-dd", // format for datepicker
      placeholder: "yyyy-mm-dd", // Placeholder for datepicker
    }
  },
  computed: {
    ...mapFields([
      'currentQuestionnaire.description',
      'currentQuestionnaire.end_date',
      'currentQuestionnaire.title',
    ]),
  },
  methods: {
    // Used in QuestionnaireCreate.
    validateForm: function() {
      const form = this.$refs.form
      return reportValidity(form)
    },
  },
  components: {
    Datepicker,
    QuestionnaireFileUpload,
    QuestionnaireFileList,
  },
})

QuestionnaireMetadataCreate.DESCRIPTION_DEFAULT = DESCRIPTION_DEFAULT
export default QuestionnaireMetadataCreate

</script>
