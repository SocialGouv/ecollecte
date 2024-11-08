<template>
  <div>
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">Etape 2 : Ajouter des questions</h2>
      </div>
      <div class="card-body pb-6">
        <info-bar>
          <p>A cette étape, vous pouvez créer votre questionnaire en ajoutant des thèmes,
          des questions et des annexes à vos questions.</p>
        </info-bar>
        <form ref="form">
          <div class="card"
               v-for="(theme, themeIndex) in themes"
               :key="'theme-' + theme.id"> <!-- Card for each theme-->
            <div class="card-status card-status-top bg-blue">
            </div>

            <div class="border-bottom">
              <div class="text-muted pt-2 pl-7" :id="'theme' + (themeIndex + 1) + 'Help'">
                Ecrivez un thème ici. 255 caractères maximum.
              </div>
              <div class="card-header border-0 pb-0 pt-0">
                <label v-bind:for="'theme' + (themeIndex + 1)" class="form-label-h3 mr-1">
                  <h2 class="card-title">{{themeIndex + 1}}.</h2>
                </label>
                <input class="form-control form-control-h3"
                       title="Ecrivez un thème ici"
                       placeholder="Ressources Humaines"
                       type="text"
                       maxlength="255"
                       v-bind:id="'theme' + (themeIndex + 1)"
                       v-model="themes[themeIndex].title"
                       oninvalid="this.setCustomValidity('Veuillez remplir ou supprimer les thèmes vides.')"
                       oninput="this.setCustomValidity('')"
                       :aria-describedby="'theme' + (themeIndex + 1) + 'Help'"
                       required>
                <span>
                  <button v-if="themes[themeIndex].questions.length === 0"
                          :id="'delete_theme_' + themeIndex"
                          @click.prevent="deleteTheme(themeIndex)"
                          role="button"
                          type="button"
                          class="btn btn-link"
                          title="Supprimer le thème"
                  >
                    <span class="fe fe-trash-2" aria-hidden="true"></span>
                    <span class="sr-only">Supprimer le thème</span>
                  </button>
                  <button v-else
                          :id="'delete_theme_' + themeIndex"
                          class="btn btn-link"
                          role="button"
                          type="button"
                          data-toggle="modal"
                          :data-target="'#deleteThemeConfirmModal' + themeIndex"
                          title="Supprimer le thème"
                  >
                    <span class="fe fe-trash-2" aria-hidden="true"></span>
                    <span class="sr-only">Supprimer le thème</span>
                  </button>
                </span>
              </div>
              <confirm-modal v-if="themes.length > 1"
                            :id="'deleteThemeConfirmModal' + themeIndex"
                             title="Confirmer la suppression de ce thème"
                             confirm-button="Oui, supprimer"
                             cancel-button="Non, retour"
                             @confirm="deleteTheme(themeIndex)"
              >
                <p>
                  <span v-if="themes[themeIndex].questions.length === 1">
                    La question associée à ce thème sera également supprimée.
                  </span>
                  <span v-else>
                    Les {{ themes[themeIndex].questions.length }} questions associées à ce thème
                    seront également supprimées.
                  </span>
                </p>
              </confirm-modal>
              <confirm-modal v-else
                            :id="'deleteThemeConfirmModal' + themeIndex"
                             title="Suppression impossible"
                             confirm-button="OK"
              >
                <p>
                  <span>
                    Le questionnaire doit contenir au moins un thème.
                  </span>
                </p>
              </confirm-modal>
            </div>

            <transition-group name="question-list" tag="div">
              <div v-for="(question, qIndex) in themes[themeIndex].questions"
                  :id="'theme-' + themeIndex + '-question-' + qIndex"
                  class="card border-0 m-0 pt-2"
                  :key="'question-' + question.id"> <!-- Card for each question -->
                <div class="text-muted pt-2 pl-9" :id="'theme' + (themeIndex + 1) + 'Help'">
                  Ecrivez une question ici.
                </div>
                <div class="card-header border-0">
                  <div class="flex-column align-items-center mr-4">
                    <button :class="{ disabled: qIndex === 0 }"
                      :tabindex="qIndex === 0 ? -1 : 0"
                      class="btn btn-secondary btn-sm move-up-button"
                      role="button"
                      type="button"
                      title="Déplacer la question vers le haut"
                      @click="moveQuestionUp(themeIndex, qIndex)">
                      <span class="fa fa-chevron-up" aria-hidden="true"></span>
                      <span class="sr-only">Déplacer la question vers le haut</span>
                    </button>
                    <div class="my-1">
                      <label v-bind:for="'question' + (themeIndex + 1) + '-' + (qIndex + 1)"
                            class="mb-0">
                        <span class="stamp stamp-md bg-blue">
                          {{ themeIndex + 1 }}.{{ qIndex + 1 }}
                        </span>
                      </label>
                    </div>
                    <button :class="{ disabled: qIndex === (theme.questions.length - 1) }"
                      :tabindex="qIndex === (theme.questions.length - 1) ? -1 : 0"
                      class="btn btn-secondary btn-sm move-down-button"
                      role="button"
                      type="button"
                      title="Déplacer la question vers le bas"
                      @click="moveQuestionDown(themeIndex, qIndex)">
                      <span class="fa fa-chevron-down" aria-hidden="true"></span>
                      <span class="sr-only">Déplacer la question vers le bas</span>
                    </button>
                  </div>
                  <textarea class="form-control"
                            title="Ecrivez une question ici"
                            placeholder="Règlement intérieur (au cours des 3 dernières années)"
                            rows="4"
                            v-bind:id="'question' + (themeIndex + 1) + '-' + (qIndex + 1)"
                            v-model="themes[themeIndex].questions[qIndex].description"
                            oninvalid="this.setCustomValidity('Veuillez remplir ou supprimer les questions vides.')"
                            oninput="this.setCustomValidity('')"
                            required>
                  </textarea>

                  <span>
                    <button v-if="themes[themeIndex].questions.length > 1"
                            :id="'delete_question_' + qIndex"
                            @click.prevent="deleteQuestion(themeIndex, qIndex)"
                            class="btn btn-link"
                            role="button"
                            type="button"
                            title="Supprimer la question"
                    >
                      <span class="fe fe-trash-2" aria-hidden="true"></span>
                      <span class="sr-only">Supprimer la question</span>
                    </button>
                    <button v-else
                            :id="'delete_question_' + qIndex"
                            class="btn btn-link"
                            role="button"
                            type="button"
                            title="Supprimer la question"
                            data-toggle="modal"
                            :data-target="'#cannot-delete-question' + themeIndex + '-' + qIndex"
                    >
                      <span class="fe fe-trash-2" aria-hidden="true"></span>
                      <span class="sr-only">Supprimer la question</span>
                    </button>
                    <confirm-modal
                            :id="'cannot-delete-question' + themeIndex + '-' + qIndex"
                             title="Suppression impossible"
                             confirm-button="OK"
                    >
                      <p>
                        <span>
                          Vous ne pouvez pas supprimer toutes les questions de ce thème.
                        </span>
                      </p>
                    </confirm-modal>
                  </span>
                  <question-file-upload :question="question"></question-file-upload>
                </div>
                <div class="card-body">
                  <question-file-list :files="question.question_files" :with-delete="true">
                  </question-file-list>
                </div>
              </div>
            </transition-group>

            <div class="card-footer">
              <button @click.prevent="addQuestion(themeIndex)"
                      id="add_question"
                      class="btn btn-primary"
                      role="button"
                      type="button"
                      title="Ajouter une question">
                <span class="fe fe-plus" aria-hidden="true"></span> Ajouter une question
              </button>
            </div>
          </div>

          <div class="card">
            <div class="card-footer">
              <div class="card-status card-status-top bg-blue">
              </div>
              <button @click="addTheme()"
                      id="add_theme"
                      class="btn btn-primary"
                      role="button"
                      type="button"
                      title="Ajouter un thème">
                <span class="fe fe-plus" aria-hidden="true"></span>Ajouter un thème
              </button>
            </div>
          </div>
        </form>

        <move-themes-modal ref="moveThemesModal">
        </move-themes-modal>

      </div>
    </div>

  </div>
</template>

<script>
import '../../css/questionnaires.css'
import Vue from 'vue'
import ConfirmModal from '../utils/ConfirmModal'
import InfoBar from '../utils/InfoBar'
import { mapFields } from 'vuex-map-fields'
import MoveThemesModal from '../themes/MoveThemesModal'
import QuestionFileList from '../questions/QuestionFileList'
import QuestionFileUpload from '../questions/QuestionFileUpload'
import reportValidity from 'report-validity'
import SwapMixin from '../utils/SwapMixin'

export default Vue.extend({
  data() {
    return {
      errors: [],
    }
  },
  computed: {
    ...mapFields([
      'currentQuestionnaire.themes',
    ]),
  },
  components: {
    ConfirmModal,
    InfoBar,
    MoveThemesModal,
    QuestionFileList,
    QuestionFileUpload,
  },
  mixins: [
    SwapMixin,
  ],
  methods: {
    addQuestion: function(themeIndex) {
      this.themes[themeIndex].questions.push({
        description: '',
        order: this.themes[themeIndex].questions.length,
      })
    },
    addTheme: function() {
      console.debug('addTheme')
      this.themes.push({ title: '', questions: [{ description: '' }] })
    },
    deleteQuestion: function(themeIndex, qIndex) {
      this.themes[themeIndex].questions.splice(qIndex, 1);
      this.swapMixin_updateOrderFields(this.themes[themeIndex].questions);
      if (this.themes[themeIndex].questions.length <= 1) {
        $("#add_question").focus();
      } else if (qIndex >= this.themes[themeIndex].questions.length) {
        $("#delete_question_"+(qIndex-1)).focus();
      } else {
        $("#delete_question_"+(qIndex+1)).focus();
      }
    },
    deleteTheme: function(themeIndex) {
      this.themes.splice(themeIndex, 1);
      this.swapMixin_updateOrderFields(this.themes);
      if (this.themes.length <= 1) {
        window.setTimeout(function() {$("#add_theme").focus();}, 300);
      } else if (themeIndex >= this.themes.length) {
        window.setTimeout(function() {$("#delete_theme_"+(themeIndex-1)).focus();}, 300);
      } else {
        window.setTimeout(function() {$("#delete_theme_"+(themeIndex)).focus();}, 300);
      }
    },
    // Used in QuestionnaireCreate.
    validateForm: function() {
      const form = this.$refs.form
      return reportValidity(form)
    },
    moveQuestionUp(themeIndex, qIndex) {
      const array = this.themes[themeIndex].questions
      const selectedJqueryElement = $('#theme-' + themeIndex + '-question-' + qIndex)
      this.swapMixin_moveItemUp(array, qIndex, selectedJqueryElement)
    },
    moveQuestionDown(themeIndex, qIndex) {
      const array = this.themes[themeIndex].questions
      const selectedJqueryElement = $('#theme-' + themeIndex + '-question-' + qIndex)
      this.swapMixin_moveItemDown(array, qIndex, selectedJqueryElement)
    },
  },
})
</script>



