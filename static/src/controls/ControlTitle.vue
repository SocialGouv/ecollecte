<template>
  <div class="card">
    <confirm-modal
      ref="modal"
      cancel-button="Annuler"
      confirm-button-prevent="Dupliquer l'espace de dépôt"
      title="Dupliquer un espace de dépôt"
      @confirm="checkUniqueReferenceCode"
    >
      <info-bar>
        <p>Veuillez sélectionner les questionnaires que vous souhaitez dupliquer.</p>
      </info-bar>
      <error-bar v-if="referenceError" :noclose="true">
        <p>Ce nom abrégé est vide ou existe déjà. Veuillez saisir un nouveau nom abrégé.</p>
      </error-bar>
      <form>
        <div class="form-group mb-4">
          <label id="reference-label" class="form-label" for="reference">
            Nom abrégé<span class="form-required">*</span>
          </label>
          <div class="flex-row align-items-center">
            <span class="input-group-prepend" id="prepend">
              <span class="input-group-text">{{new Date().getFullYear()}}_</span>
            </span>
            <input id="reference"
                   type="text"
                   class="form-control"
                   v-model="reference_code"
                   required aria-labelledby="reference-label"
                   maxlength="25"
                   title="Ce champ ne doit pas contenir de caractères spéciaux
                         ( ! , @ # $ / \ ' &quot; + etc)"
                   @focus="referenceChanged">
          </div>
          <span class="text-danger" v-if="reference_code.length > 24">
            <p>Ce champ ne peut contenir plus de 25 caractères.</p>
          </span>
        </div>
        <div class="form-group mb-6">
          <label class="custom-control custom-checkbox">
            <input type="checkbox" class="custom-control-input" @click="checkAllQuestionnaires" v-model="allChecked">
            <span class="custom-control-label font-weight-bold">Sélectionner Tout
          </label>
          <label v-for="q in accessibleQuestionnaires"
                :for="q.id"
                :key="q.id"
                class="custom-control custom-checkbox">
            <input :id="q.id" type="checkbox" class="custom-control-input" :value="q.id" v-model="checkedQuestionnaires">
            <span class="custom-control-label">Questionnaire {{ q.numbering }} - {{ q.title }}</span>
          </label>
        </div>
      </form>
    </confirm-modal>
    <confirm-modal
      ref="modalexp"
      cancel-button="Annuler"
      confirm-button-prevent="Exporter l'espace de dépôt"
      title="Exporter un espace de dépôt"
      @confirm="exportControl"
    >
      <info-bar>
        <p>Veuillez sélectionner les questionnaires dont vous souhaitez exporter les fichiers-réponses.</p>
      </info-bar>
      <form>
        <div class="form-group mb-6">
          <label for="checkAll" class="custom-control custom-checkbox">
            <input id="checkAll" type="checkbox" class="custom-control-input" @click="checkAllQuestionnaires" v-model="allChecked">
            <span class="custom-control-label font-weight-bold">Sélectionner Tout
          </label>
          <label v-for="q in accessibleQuestionnaires"
                :for="q.id"
                :key="q.id"
                class="custom-control custom-checkbox">
            <input :id="q.id" type="checkbox" class="custom-control-input" :value="q.id" v-model="checkedQuestionnaires">
            <span class="custom-control-label">Questionnaire {{ q.numbering }} - {{ q.title }}</span>
          </label>
        </div>
      </form>
    </confirm-modal>
    <div
      v-if="this.loaderActive"
      class="loader-container"
    >
      <div class="loader-wrapper">
        <div class="loader"></div>
        <p>Téléchargement en cours</p>
      </div>
    </div>
    <div class="card-status card-status-top bg-blue"></div>
    <template v-if="editMode">
      <div class="card-body">
        <error-bar v-if="hasErrors" :noclose="true">
            <p>L'espace de dépôt n'a pas pu être modifié. Erreur : {{JSON.stringify(errors)}}</p>
        </error-bar>

        <form @submit.prevent="updateControl">
          <h2 class="card-title">Modifier l'espace de dépôt</h2>
          <div class="form-fieldset">
            <div class="form-group">
              <label id="organization-label" class="form-label" for="organisme">
                Quel est le nom de l’organisme qui va déposer les réponses ?
                <span class="form-required">*</span>
              </label>
              <div class="flex-row align-items-center">
                <span class="fa fa-building mr-2 text-muted" aria-hidden="true"></span>
                <input id="organisme" type="text" class="form-control" v-model="organization" required aria-labelledby="organization-label" maxlength="255">
              </div>
            </div>
            <div class="form-group">
              <label id="title-label" class="form-label" for="procedure">
                Quel est le nom de la procédure pour laquelle vous ouvrez cet espace de dépôt ?
                <span class="form-required">*</span>
              </label>
              <div class="flex-row align-items-center">
                <span class="fa fa-award mr-2 text-muted" aria-hidden="true"></span>
                <input id="procedure" type="text" class="form-control" v-model="title" required aria-labelledby="title-label" maxlength="255">
              </div>
            </div>
            <div class="form-group form-check">
              <input id="is-model" type="checkbox" class="form-check-input" v-model="isModel">
              <label class="form-check-label" for="is-model">
                Marquer comme modèle
              </label>
            </div>
          </div>
          <div class="text-right">
            <button @click="cancel"
                    type="button"
                    class="btn btn-secondary">
              Annuler
            </button>
            <button id="control-title-submit-button"
                    type="submit"
                    class="btn btn-primary">
              Modifier l'espace de dépôt
            </button>
          </div>
        </form>

      </div>
    </template>

    <template v-else>
      <div class="card-body flex-row justify-content-between">

        <div v-if="organization">
          <div class="mb-3">
            <div class="text-muted font-italic">
              <span class="fa fa-building mr-2" aria-hidden="true"></span>
              Organisme interrogé
            </div>
            <div class="page-title">{{ organization }}</div>
          </div>
          <div class="mb-3">
            <div class="text-muted font-italic">
              <span class="fa fa-award mr-2" aria-hidden="true"></span>
              Procédure
            </div>
            <div class="card-title">{{ title }}</div>
          </div>
          <div class="mb-3">
            <div class="text-muted font-italic">
              <span class="fa fa-user mr-2" aria-hidden="true"></span>
              Accès
            </div>
            <div class="card-title">{{ getAccessTypeLibelle() }}</div>
          </div>
          <div v-if="accessType === 'demandeur' && isModel" class="mb-3">
            <div class="text-success font-italic">
              <span class="fa fa-check mr-2" aria-hidden="true"></span>
              Marqué comme modèle
            </div>
          </div>
        </div>
        <div v-else>
          <div class="page-title">{{ title }}</div>
        </div>

        <div class="col-4 flex-column ie-flex-column-fix align-items-end ml-6">
          <div v-if="accessType === 'demandeur'" class="btn-group">
            <button type="button"
                    class="btn btn-secondary"
                    @click="enterEditMode">
              <span class="fe fe-edit mr-2" aria-hidden="true"></span>
              Modifier
            </button>
            <button type="button"
                    class="btn btn-secondary dropdown-toggle dropdown-toggle-split"
                    data-toggle="dropdown"
                    aria-haspopup="true"
                    aria-expanded="false">
              <span class="sr-only">Menu d'actions</span>
            </button>
            <div class="dropdown-menu dropdown-menu-right">
              <button
                      v-if="this.accessibleQuestionnaires.length > 0 && sessionUser.is_inspector"
                      class="dropdown-item"
                      type="button"
                      @click="showCloneModal"
              >
                <span class="fe fe-copy mr-2" aria-hidden="true"></span>
                Dupliquer
            </button>
              <button class="dropdown-item"
                      type="button"
                      @click="showExportModal"
              >
                <span class="fas fa-file-export mr-2" aria-hidden="true"></span>
                Exporter (.zip)
              </button>

              <button v-if="!isModel" 
                class="dropdown-item"
                type="button"
                @click="markAsModel"
              >
               <span class="far fa-file-alt" aria-hidden="true"></span>
                  Marquer comme modèle
              </button>
              <button class="dropdown-item text-danger"
                      type="button"
                      @click="startControlDeleteFlow"
              >
                <span class="fe fe-trash-2 mr-2" aria-hidden="true"></span>
                Supprimer cet espace...
              </button>
            </div>
          </div>
        </div>

      </div>
    </template>

    <control-delete-flow ref="controlDeleteFlow" :control="control"></control-delete-flow>

  </div>
</template>

<script>
import '../../css/controls.css'
import { mapState } from 'vuex'
import { mapFields } from 'vuex-map-fields'
import axios from 'axios'
import backendUrls from '../utils/backend'
import Vue from 'vue'
import ControlDeleteFlow from './ControlDeleteFlow'

import ConfirmModal from '../utils/ConfirmModal'
import InfoBar from '../utils/InfoBar'
import ErrorBar from '../utils/ErrorBar'

import JSZip from 'jszip'
import JSZipUtils from 'jszip-utils'
import { saveAs } from 'file-saver'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

export default Vue.extend({
  props: {
    control: { type: Object, default: () => ({}) },
    accessType: { type: String, default: '' },
  },
  data: function() {
    return {
      editMode: false,
      title: '',
      organization: '',
      isModel: false, 
      errors: '',
      hasErrors: false,
      referenceError: false,
      reference_code: '',
      allChecked: false,
      checkedQuestionnaires: [],
      users: [],
      loaderActive: false,
    }
  },
  computed: {
    ...mapState({
      controls: 'controls',
    }),
    ...mapFields([
      'sessionUser',
    ]),
    accessibleQuestionnaires() {
      return this.control.questionnaires.filter(q => !q.is_draft)
    },
  },
  components: {
    InfoBar,
    ErrorBar,
    ControlDeleteFlow,
    ConfirmModal,
  },
  mounted() {
    this.getUsers()
    this.restoreForm()
  },
  methods: {
    showCloneModal() {
      this.allChecked = false
      this.reference_code = ''
      this.checkedQuestionnaires = []
      $(this.$refs.modal.$el).modal('show')
    },
    hideCloneModal() {
      $(this.$refs.modal.$el).modal('hide')
    },
    referenceChanged() {
      this.referenceError = false
    },
    getUsers() {
      axios.get(backendUrls.getUsersInControl(this.control.id))
        .then((response) => {
          this.users = response.data
        })
    },
    checkUniqueReferenceCode() {
      // reference code given by user (2021_SOMETHING)
      const newRefCode = new Date().getFullYear() + '_' + this.reference_code
      this.referenceError = false
      axios.get(backendUrls.checkControlUniqueCode(this.control.id, newRefCode))
        .then((response) => {
          if (response.data === 'True') {
            this.referenceError = true
            return
          }
          this.cloneControl(newRefCode)
        })
    },
    getAccessTypeLibelle() {
      if (this.accessType === 'demandeur') {
        return 'Demandeur'
      }
      return 'Répondant'
    },
    cloneControl(newRefCode) {

      this.markAsModel()

      const valid = this.reference_code &&
                    !this.controls.find(ctrl => ctrl.reference_code === newRefCode)

      if (!valid) {
        this.referenceError = true
        return
      }

      const getCreateMethodCtrl = () => axios.post.bind(this, backendUrls.control())

      if (this.checkedQuestionnaires.length) {
        console.log(" idCtlSource ",this.control.id)
        const questionnaires = this.accessibleQuestionnaires
          .filter(aq => this.checkedQuestionnaires.includes(aq.id))
        const ctrl = {
          idCtlSource:this.control.id,
          title: this.control.title,
          depositing_organization: this.control.depositing_organization,
          reference_code: newRefCode,
          questionnaires: questionnaires,
        }
       
        getCreateMethodCtrl()(ctrl).then(async response => {
          // Copy users for new control
          
          const controlId = response.data.id
         
          /*this.users
            .filter(u => u.profile_type === 'inspector')
            .map(i => {
              const inspector = { ...i, control: controlId }
              axios.post(backendUrls.user(), inspector)
          })*/
        
        const resp = await axios.get(backendUrls.getQuestionnaireAndThemesByCtlId(this.control.id))
        this.control = resp.data.filter(obj => obj.id === this.control.id)[0]

        this.accessibleQuestionnaires = this.control.questionnaires
          .filter(aq => this.checkedQuestionnaires.includes(aq.id))

          const promises = this.accessibleQuestionnaires
            .filter(aq => this.checkedQuestionnaires.includes(aq.id))
            .map(q => {
              const themes = q.themes.map(t => {
                const qq = t.questions.map(q => { return { description: q.description } })
                return { title: t.title, questions: qq }
              })

              const newQ = { ...q, control: controlId, is_draft: true, is_replied:false, has_replies:false, is_finalized:false, id: null, themes: [] }
              return this.cloneQuestionnaire(newQ, themes, q.themes)
            })

          Promise.all(promises).then((values) => {
            setTimeout(() => { window.location.href = backendUrls.home(); }, 3000);
          });
        })

        this.hideCloneModal()
      }
    },
    async cloneQuestionnaire(questionnaire, themes, oldThemes) {
      const getCreateMethod = () => axios.post.bind(this, backendUrls.questionnaire())
      const getUpdateMethod = (qId) => axios.put.bind(this, backendUrls.questionnaire(qId))

      const promise = await getCreateMethod()(questionnaire).then(async response => {
        const qId = response.data.id
        const newQ = { ...questionnaire, themes: themes }

          newQ.questionnaire_files.map(qf => {
                axios.get(qf.url, { responseType: 'blob' }).then(response => {
                  const formData = new FormData()
                  formData.append('file', response.data, qf.basename)
                  formData.append('questionnaire', qId)
                  axios.post(backendUrls.piecejointe(), formData, {
                    headers: {
                      'Content-Type': 'multipart/form-data',
                    },
                  })
                })
              }) 

        await getUpdateMethod(qId)(newQ).then(response => {
          const updatedQ = response.data

          oldThemes.map(t => {
            t.questions.map(q => {
              const qId = updatedQ.themes.find(updatedT => updatedT.order === t.order)
                .questions.find(updatedQ => updatedQ.order === q.order).id

              q.question_files.map(qf => {
                axios.get(qf.url, { responseType: 'blob' }).then(response => {
                  const formData = new FormData()
                  formData.append('file', response.data, qf.basename)
                  formData.append('question', qId)
                  axios.post(backendUrls.annexe(), formData, {
                    headers: {
                      'Content-Type': 'multipart/form-data',
                    },
                  })
                })
              })
            })
          })
        })
      })

      return promise
    },
    showExportModal() {
      this.allChecked = false;
      this.checkedQuestionnaires = []
      $(this.$refs.modalexp.$el).modal('show')
    },
    markAsModel() {
      this.clearErrors()
      const payload = {
        title: this.title,
        depositing_organization: this.organization,
        is_model: true
      }
      axios.put(backendUrls.control(this.control.id), payload)
        .then(response => {
          console.debug(response)
          this.title = response.data.title
          this.organization = response.data.depositing_organization
          this.isModel = response.data.is_model
          console.log("Marquer comme modèle : ", response.data)
        })
        .catch((error) => {
          console.error(error)
          this.errors = error.response.data
          this.hasErrors = true
        })
  },

    hideExportModal() {
      $(this.$refs.modalexp.$el).modal('hide')
    },
    checkAllQuestionnaires() {
      this.checkedQuestionnaires = []
      this.allChecked = !this.allChecked

      if (this.allChecked) {
        this.accessibleQuestionnaires.map(q => {
          this.checkedQuestionnaires.push(q.id)
        })
      }
    },
  async exportControl() {
  if (!this.checkedQuestionnaires.length) {
    this.hideExportModal();
    return;
  }

  this.loaderActive = true;

  const formatFilename = (file) => {
    const questionnaireNb = String(file.questionnaireNb).padStart(2, '0')
    const questionnaireId = `Q${questionnaireNb}`;
    let themeId = '';
    let filename = ''
    if (file.category == 'question_file') {
      themeId = 'ANNEXES-AUX-QUESTIONS';
      filename = `Q${questionnaireNb}-${file.basename}`;
    } else if (file.is_deleted) {
      themeId = 'CORBEILLE';
      filename = `Q${questionnaireNb}-${file.basename}`;
    } else {
      themeId = 'T' + String(file.themeId + 1).padStart(2, '0');
      const questionId = String(file.questionId + 1).padStart(2, '0');
      filename = `Q${questionnaireNb}-${themeId}-${questionId}-${file.basename}`;
    }
    return { questionnaireId, themeId, filename };
  };

  try {
    const resp = await axios.get(backendUrls.getQuestionnaireAndThemesByCtlId(this.control.id));
    this.control = resp.data.filter(obj => obj.id === this.control.id)[0];
    const filteredQuestionnaires = this.control.questionnaires.filter(aq => this.checkedQuestionnaires.includes(aq.id));
    let files = [];

    for (const fq of filteredQuestionnaires) {
      if (fq.themes) {
        for (const t of fq.themes) {
          if (t.questions) {
            for (const q of t.questions) {
              if (q.response_files) {
                for (const rf of q.response_files) {
                  if (rf) {
                    files.push({
                      questionnaireNb: fq.numbering,
                      themeId: t.order,
                      questionId: q.order,
                      category: 'response_file',
                      basename: rf.basename,
                      url: rf.url,
                      is_deleted: rf.is_deleted,
                    });
                  }
                }
              }
            }
          }
        }
      }
    }

    for (const fq of filteredQuestionnaires) {
      if (fq.themes) {
        for (const t of fq.themes) {
          if (t.questions) {
            for (const q of t.questions) {
              if (q.question_files) {
                for (const qf of q.question_files) {
                  if (qf) {
                    files.push({
                      questionnaireNb: fq.numbering,
                      themeId: t.order,
                      questionId: q.order,
                      category: 'question_file',
                      basename: qf.basename,
                      url: qf.url,
                      is_deleted: qf.is_deleted,
                    });
                    
                  }
                }
              }
            }
          }
        }
      }
    }

    const zipFilename = this.control.reference_code + '.zip';
    const zip = new JSZip();
    let cnt = 0;

    if (files.length === 0) {
      this.loaderActive = false;
    }

    files.forEach(file => {
      const url = window.location.origin + file.url;
      JSZipUtils.getBinaryContent(url, (err, data) => {
        if (err) throw err;
        const formatted = formatFilename(file);
        zip.folder(formatted.questionnaireId)
          .folder(formatted.themeId)
          .file(formatted.filename, data, { binary: true });

        cnt++;
        if (cnt === files.length) {
          zip.generateAsync({ type: 'blob' }).then((content) => {
            this.loaderActive = false;
            saveAs(content, zipFilename);
          });
        }
      });
    });

    this.hideExportModal();
  } catch (error) {
    console.error('Error exporting control:', error);
    this.loaderActive = false;
    this.hideExportModal();
  }
},

    restoreForm() {
      this.title = this.control.title
      this.organization = this.control.depositing_organization
      this.isModel = this.control.is_model
    },
    clearErrors() {
      this.errors = ''
      this.hasErrors = false
    },
    enterEditMode() {
      this.clearErrors()
      this.editMode = true
    },
    quitEditMode() {
      this.clearErrors()
      this.editMode = false
    },
    cancel() {
      this.restoreForm()
      this.quitEditMode()
    },
    updateControl: function() {
      this.clearErrors()
      const payload = {
        title: this.title,
        depositing_organization: this.organization,
        is_model: this.isModel
      }
      axios.put(backendUrls.control(this.control.id), payload)
        .then(response => {
          console.debug(response)
          this.title = response.data.title
          this.organization = response.data.depositing_organization
          this.isModel = response.data.is_model
          console.log("Marquer comme modèle : ", response.data)

          // Display a "loading" spinner on clicked button, while the page reloads, so that they know their click
          // has been registered.
          $('#control-title-submit-button').addClass('btn-loading')
          window.location.reload()
        })
        .catch((error) => {
          console.error(error)
          this.errors = error.response.data
          this.hasErrors = true
        })
    },
    startControlDeleteFlow() {
      this.$refs.controlDeleteFlow.start()
    },
  },
})

</script>