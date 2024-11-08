<template>
  <div class="card">
    <div class="card-status card-status-top bg-blue"></div>
    <div class="card-header">
      <h2 class="card-title">
        <span class="fe fe-users mr-2" aria-hidden="true"></span>
        <span>Qui a accès à cet espace ?</span>
      </h2>
    </div>

    <div class="card-body">
      <div class="card">
        <div class="card-header justify-content-between">
          <h2 class="card-title">
            <span class="fa fa-university mr-2" aria-hidden="true"></span>
            <strong>Équipe d'instruction</strong>
          </h2>
          <button v-if="accessType === 'demandeur'"
                  data-toggle="modal"
                  data-target="#addUserModal"
                  @click="updateEditingState('inspector')"
                  class="btn btn-primary">
            <span class="fe fe-plus" aria-hidden="true"></span>
            Ajouter un demandeur
          </button>
        </div>
        <user-list :users="inspectorUsers" profile-type="inspector"
          :control="control" :accessType="accessType">
        </user-list>
      </div>

      <div class="card mb-0">
        <div class="card-header justify-content-between">
          <h2 class="card-title">
            <span class="fa fa-building mr-2" aria-hidden="true"></span>
            <strong>Organisme interrogé</strong>
          </h2>
          <button v-if="accessType === 'demandeur'"
                  data-toggle="modal"
                  data-target="#addUserModal"
                  @click="updateEditingState('audited')"
                  class="btn btn-primary">
            <span class="fe fe-plus" aria-hidden="true"></span>
            Ajouter un répondant
          </button>
        </div>
        <user-list :users="auditedUsers" profile-type="audited"
          :control="control" :accessType="accessType">
        </user-list>
      </div>
    </div>
  </div>

</template>

<script lang="ts">
import axios from 'axios'
import backendUrls from '../utils/backend'
import EventBus from '../events'
import { mapFields } from 'vuex-map-fields'
import { store } from '../store'
import UserList from './UserList'
import Vue from 'vue'

export default Vue.extend({
  store,
  props: {
    control: { type: Object, default: () => ({}) },
    accessType: { type: String, default: '' },
  },
  data() {
    return {
      auditedUsers: [],
      inspectorUsers: [],
    }
  },
  computed: {
    ...mapFields([
      'editingControl',
      'editingProfileType',
      'sessionUser',
    ]),
  },
  methods: {
    getAuditedUsers() {
      axios.get(backendUrls.getAuditedUsersInControl(this.control.id))
        .then((response) => {
          this.auditedUsers = response.data
        })
    },
    getInspectorUsers() {
      axios.get(backendUrls.getInspectorUsersInControl(this.control.id))
        .then((response) => {
          this.inspectorUsers = response.data
        })
    },
    updateEditingState(profileType) {
      this.editingControl = this.control
      this.editingProfileType = profileType
    },
  },
  mounted() {
    this.getAuditedUsers()
    this.getInspectorUsers()
    EventBus.$on('users-changed', () => {
      this.getAuditedUsers()
      this.getInspectorUsers()
    })
  },
  components: {
    UserList,
  },
})
</script>
