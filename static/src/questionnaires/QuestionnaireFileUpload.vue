<template>
<div>
  <error-bar v-if="errorMessage" @dismissed="clearError">
    <p>{{ errorMessage }}</p>
  </error-bar>
  <div v-if="questionnaire.id">
    <label class="btn btn-primary">
      <span class="fe fe-upload mr-2"></span>
      Ajouter une pièce jointe
      <input type="file" ref="fileInput" v-on:change="handleFileUpload()" hidden/>
    </label>
  </div>
  <div v-else>
    <label class="btn btn-primary disabled" >
      <span class="fe fe-upload mr-2" ></span>
      Ajouter une pièce jointe
    </label>
    <div class="small">
      Pour pouvoir ajouter des pièces jointes,
    </div>
    <div class="small">
      vous devez d'abord enregistrer
    </div>
    <div class="small">
      votre brouillon.
    </div>
  </div>
</div>
</template>

<script>
import axios from 'axios'
import backendUrls from '../utils/backend'
import ErrorBar from '../utils/ErrorBar'
import Vue from 'vue'

export default Vue.extend({
  props: {
    questionnaire: { type: Object, default: () => ({}) },
  },
  data () {
    return {
      errorMessage: undefined,
      file: '',
    }
  },
  components: {
    ErrorBar,
  },
  methods: {
    clearError() {
      this.errorMessage = undefined
    },
    handleFileUpload() {
      this.file = this.$refs.fileInput.files[0]
      this.submitFile()
    },
    submitFile() {
      this.clearError()
      const formData = new FormData()
      formData.append('file', this.file)
      formData.append('questionnaire', this.questionnaire.id)
      axios.post(
        backendUrls.piecejointe(),
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        .then(response => {
          console.debug('QuestionnaireFileUpload response', response)
          const newFile = response.data
          this.questionnaire.questionnaire_files.push(newFile)
        })
        .catch(error => {
          console.log('Error when posting questionnaire file', error)
         if (error.response && Array.isArray(error.response.data)) {
          this.errorMessage = error.response.data[0] ;
        } else {
          this.errorMessage = 'La pièce jointe n\'a pu être sauvée.'
        }
          
        })
    },
  },
})
</script>
