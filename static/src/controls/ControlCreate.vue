<template>
  <div>
    <button id="AddControlButton" class="btn btn-primary" @click="showModal" ref="addControlButton"
            aria-expanded="false"
            aria-controls="modal">
      <span class="fe fe-plus" aria-hidden="true"></span>
      Ajouter un espace de dépôt
    </button>

    <confirm-modal-with-wait ref="modal"
                             cancel-button="Annuler"
                             confirm-button="Créer l'espace de dépôt"
                             title="Créer un nouvel espace de dépôt"
                             aria-labelledby="dialog1_label"
                             @confirm="createControl"
                             @close="closeModal"
    >
      <div>
        <info-bar>
          <p>Chaque espace de dépôt ne sera visible que pour les personnes que vous inviterez.</p>
        </info-bar>
        <info-bar>
          <p>Tous Les champs sont obligatoires.</p>
        </info-bar>
          <div class="form-group mb-6">
            <label id="title-label" for="nom_controle" class="form-label">
              Quel est le nom de la procédure pour laquelle vous ouvrez cet espace de dépôt ?
              <span class="form-required">*</span>
            </label>
            <div id="title-help" class="text-muted">
              <p>Exemple : Contrôle des comptes et de la gestion de la Fédération Française de Football. 255 caractères maximum.</p>
            </div>
            <div class="flex-row align-items-center">
              <span class="fa fa-award mr-2 text-muted" aria-hidden="true"></span>
              <input type="text"
                     id="nom_controle"
                     ref="nom_controle"
                     class="form-control"
                     v-model="title"
                     maxlength="255"
                     required
                     aria-describedby="title-help"
                     aria-labelledby="title-label">
            </div>
          </div>

          <div class="form-group mb-6">
            <label id="organization-label" for="organisation_controle" class="form-label">
              Quel est le nom de l’organisme qui va déposer les réponses ?
              <span class="form-required">*</span>
            </label>
            <div id="organization-help" class="text-muted">
              <p>Exemple : Ministère des Sports. 255 caractères maximum.</p>
            </div>
            <div class="flex-row align-items-center">
              <span class="fa fa-building mr-2 text-muted" aria-hidden="true"></span>
              <input type="text"
                     id="organisation_controle"
                     class="form-control"
                     v-model="organization"
                     maxlength="255"
                     required
                     aria-describedby="organization-help"
                     aria-labelledby="organization-label">
            </div>
          </div>

          <div class="form-group mb-6">
            <label id="reference-code-label" for="reference_controle" class="form-label">
              Indiquez un nom abrégé pour cet espace de dépôt :
              <span class="form-required">*</span>
            </label>
            <div id="reference-code-help" class="text-muted">
              <p>Ce nom sera celui du dossier contenant les pièces déposées. Il apparaîtra lors de
              l'export de l'espace de dépôt. Nous conseillons un nom court (max 25 caractères) et signifiant,
              pour que vous retrouviez facilement le dossier. Exemple : FFF_MinSports</p>
            </div>
            <div class="input-group">
            <span class="input-group-prepend" id="basic-addon3">
              <span class="input-group-text">{{ reference_code_prefix }}</span>
            </span>
              <input type="text"
                     id="reference_controle"
                     class="form-control"
                     v-model="reference_code_suffix" required
                     pattern="^[\.\s\wÀ-ÖØ-öø-ÿŒœ-]+$"
                     maxlength="25"
                     title="Ce champ ne doit pas contenir de caractères spéciaux
                         ( ! , @ # $ / \ ' &quot; + etc)"
                     aria-describedby="reference-code-help"
                     aria-labelledby="reference-code-label">
            </div>
            <span class="text-danger" v-if="reference_code_suffix.length > 24">
              <p>Ce champ ne peut contenir plus de 25 caractères.</p>
            </span>
          </div>

          <div class="form-group mb-6">
            <label id="title-label" for="nom_controle" class="form-label">
              Sélectionnez un espace de dépôt modèle :
            </label>
          
            <div class="flex-row align-items-center">
              <span class="far fa-file-alt mr-2 text-muted" aria-hidden="true"></span>
              <select
                id="nom_controle"
                v-model="selectedModel"
                class="form-control"
                aria-labelledby="title-label"
              >
                <option value="">Sélectionnez un modèle</option>
                <option v-for="model in models" :key="model.id" :value="model.id">
                  {{ model.reference_code }}
                </option>
              </select>
            </div>
          </div>

      </div>
    </confirm-modal-with-wait>
  </div>
</template>

<script>
import axios from 'axios'
import Vue from 'vue'

import backendUrls from '../utils/backend'
import ConfirmModalWithWait from '../utils/ConfirmModalWithWait'
import InfoBar from '../utils/InfoBar'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

export default Vue.extend({
  data: function() {
    return {
      title: '',
      organization: '',
      reference_code_suffix: '',
      year: new Date().getFullYear(),
      isModalOpen: false, 
      models: [], 
      selectedModel: "" ,
      referenceError: false,
      controlId:null,
    }
  },
  created() {
    this.loadModels(); 
  },
  computed: {
    reference_code_prefix: function () {
      return this.year + '_'
    },
  },
  components: {
    ConfirmModalWithWait,
    InfoBar,
  },
  methods: {
    showModal() {
      this.isModalOpen = true;
      this.$refs.addControlButton.setAttribute('aria-expanded', 'true');
      $(this.$refs.modal.$el).modal('show');
      $(this.$refs.modal.$el).on("hidden.bs.modal", this.closeModal);
      this.$nextTick(() => {
        this.$refs["nom_controle"].focus();
      });
    },
    closeModal() {
      this.isModalOpen = false;
      this.$refs.addControlButton.setAttribute('aria-expanded', 'false');
      $(this.$refs.modal.$el).modal('hide');
      this.$nextTick(() => {
        this.$refs.addControlButton.focus();
      });
    },
    loadModels() {
      axios
        .get(backendUrls.getControlsList())
        .then((response) => {
          this.models = response.data.filter((control) => control.is_model === true);
        })
        .catch((error) => {
          console.error("Erreur lors du chargement des modèles :", error);
        });
    },
    createControl: function(processingDoneCallback) {
      if (this.selectedModel) {
        console.log('createControlWithModel ')
        this.createControlWithModel(processingDoneCallback, this.selectedModel);
      }else{
        console.log('createControlWithoutModel ')
        const payload = {
          title: this.title,
          depositing_organization: this.organization,
          reference_code: this.reference_code_prefix + this.reference_code_suffix,
        }
        axios.post(backendUrls.control(), payload)
          .then(response => {
            console.debug(response);
            processingDoneCallback(null, response, backendUrls.home());
          })
          .catch((error) => {
            console.error('Error creating control', error)
            const errorMessage = this.makeErrorMessage(error)
            processingDoneCallback(errorMessage)
          })
     } 
    },
    createControlWithModel: async function (processingDoneCallback, modelControlId) {
      try {
        const payload = {
          title: this.title,
          depositing_organization: this.organization,
          reference_code: this.reference_code_prefix + this.reference_code_suffix,
        };

        const controlResponse = await axios.post(backendUrls.control(), payload);
        this.controlId = controlResponse.data.id;

        try {
          await this.createQuestionnaire(modelControlId, this.controlId);
        } catch (questionnaireError) {
          console.error('Error creating questionnaire', questionnaireError);
          return processingDoneCallback('Erreur lors de la création du questionnaire.');
        }

        processingDoneCallback(null, controlResponse, backendUrls.home());
      } catch (error) {
        console.error('Error creating control', error);
        const errorMessage = this.makeErrorMessage(error);
        processingDoneCallback(errorMessage);
      }
    },

  async createQuestionnaire(modelControlId, controlId) {
    try {
      const response = await axios.get(backendUrls.getQuestionnaireAndThemesByCtlId(modelControlId));
      const data = response.data;

      if (!data || !Array.isArray(data)) {
        console.error('Erreur :', data);
        return;
      }

      for (const control of data) {
        for (const questionnaire of control.questionnaires) {
          const themes = questionnaire.themes.map((theme) => {
            const questions = theme.questions.map((question) => ({
              description: question.description,
              question_files: question.question_files,
            }));

            return {
              title: theme.title,
              order: theme.order,
              questions,
            };
          });

          const newQuestionnaire = {
            ...questionnaire,
            control: controlId,
            is_draft: true,
            is_replied: false,
            has_replies: false,
            is_finalized: false,
            id: null,
            themes,
          };

          const createMethod = () => axios.post(backendUrls.questionnaire(), newQuestionnaire);
          const updateMethod = (qId) => axios.put(backendUrls.questionnaire(qId), newQuestionnaire);

          try {
            const res = await createMethod();
            const qId = res.data.id;
            
            for (const qf of newQuestionnaire.questionnaire_files) {
              const fileResponse = await axios.get(qf.url, { responseType: 'blob' });
              const formData = new FormData();
              formData.append('file', fileResponse.data, qf.basename);
              formData.append('questionnaire', qId);

              await axios.post(backendUrls.piecejointe(), formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
              });
            }

            const updatedQuestionnaire = { ...newQuestionnaire, id: qId };
            const updateResponse = await updateMethod(qId);
            const updatedThemes = updateResponse.data.themes;

            for (const updatedTheme of updatedThemes) {
              const originalTheme = themes.find((t) => t.order === updatedTheme.order);

              for (const originalQuestion of originalTheme.questions) {
                const updatedQuestion = updatedTheme.questions.find(
                  (uq) => uq.order === originalQuestion.order
                );

                for (const qf of originalQuestion.question_files) {
                  const fileResponse = await axios.get(qf.url, { responseType: 'blob' });
                  const formData = new FormData();
                  formData.append('file', fileResponse.data, qf.basename);
                  formData.append('question', updatedQuestion.id);

                  await axios.post(backendUrls.annexe(), formData, {
                    headers: { 'Content-Type': 'multipart/form-data' },
                  });
                }
              }
            }

          } catch (err) {
            console.error('Erreur lors de la création du questionnaire :', err);
          }
        }
      }
    } catch (error) {
      console.error('Erreur lors de la création des questionnaires :', error);
    }
  },

    makeErrorMessage: function (error) {
      if (error.response && error.response.data && error.response.data.reference_code) {
        const requestedCode = JSON.parse(error.response.config.data).reference_code
        if (error.response.data.reference_code[0] === 'UNIQUE') {
          return 'Le nom abrégé "' + requestedCode +
                '" existe déjà pour un autre espace. Veuillez en choisir un autre.'
        }
        if (error.response.data.reference_code[0] === 'INVALID') {
          return 'Le nom abrégé "' + requestedCode +
                 '" ne doit pas contenir de caractères spéciaux (! , @ # $ / \\ " \' + etc).' +
                 ' Veuillez en choisir un autre.'
        }
      }

      if (error.message && error.message === 'Network Error') {
        return "L'espace de dépôt n'a pas pu être créé. Erreur : problème de réseau"
      }

      if (error.message) {
        return "L'espace de dépôt n'a pas pu être créé. Erreur : " + error.message
      }

      return "L'espace de dépôt n'a pas pu être créé."
    },
  },
})

</script>
