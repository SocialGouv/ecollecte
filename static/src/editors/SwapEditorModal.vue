<template>
    <div class="modal" tabindex="-1" role="dialog">
      <div class="modal-dialog large-modal" role="document">
        <div class="modal-content">
          <div class="modal-header border-bottom-0">
            <span class="fa fa-exchange-alt mr-2 mt-3" aria-hidden="true"></span>
            <div id="modal_title" class="modal-title">
                Transférer les droits de rédaction du questionnaire
            </div>
            <button type="button"
                    class="close"
                    data-dismiss="modal"
                    aria-label="Fermer">
                    <span class="sr-only">Fermer</span>
            </button>
          </div>

          <div class="modal-body">
            <p class="mx-5">
              <strong>À qui souhaitez-vous transférer les droits de rédaction de ce questionnaire ?</strong>
            </p>

            <error-bar v-if="errorMessage"
                       class="mx-5">
              <p>{{ errorMessage }}</p>
            </error-bar>

            <div class="card-body">
              <div class="card">
                <div class="card-body">
                  <div class="flex-row align-items-center">
                    <div class="flex-column mr-4 flex-grow-1">
                      <strong>Libérer les droits de rédaction pour toute l'équipe</strong>
                      <p>Chacun.e de vos collègues pourra à son tour les prendre pour rédiger.</p>
                    </div>
                    <div class="flex-column mr-4">
                      <button
                        class="btn btn-primary"
                        title="Transférer"
                        @click="unsetEditor()">
                          <span class="fa fa-lock-open mr-2" aria-hidden="true"></span>
                          Libérer les droits
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="card">
                <div class="card-header justify-content-between">
                  <h2 class="card-title"><span class="fa fa-university mr-2" aria-hidden="true"></span><strong>Équipe d'instruction</strong></h2>
                </div>

                <editor-list :users="inspectorUsers()"
                             :questionnaireId='questionnaireId'
                             @swap-editor="swapEditor">
                </editor-list>
              </div>

              <contact-support></contact-support>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import '../../css/editors.css'
import { mapFields } from 'vuex-map-fields'
import axios from 'axios'
import backendUrls from '../utils/backend.js'
import ContactSupport from '../utils/ContactSupport'
import EditorList from './EditorList'
import ErrorBar from '../utils/ErrorBar'
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default Vue.extend({
  props: [
    'controlId',
    'questionnaireId',
  ],
  data() {
    return {
      users: [],
      errorMessage: undefined,
    }
  },
  computed: {
    ...mapFields(['sessionUser']),
  },
  methods: {
    getUsers() {
      axios.get(backendUrls.getUsersInControl(this.controlId))
        .then((response) => {
          this.users = response.data
        })
    },
    inspectorUsers() {
      return this.users.filter(item => {
        return item.profile_type === 'inspector' & item.id !== this.sessionUser.id
      })
    },
    swapEditor(user) {
      this.errorMessage = undefined
      this.$emit('swap-editor', user)
    },
    unsetEditor() {
      this.errorMessage = undefined
      this.$emit('unset-editor')
    },
    showError(errorMessage) {
      this.errorMessage = errorMessage
    },
  },
  components: {
    ContactSupport,
    EditorList,
    ErrorBar,
  },
  mounted() {
    this.getUsers()
  },
})
</script>
