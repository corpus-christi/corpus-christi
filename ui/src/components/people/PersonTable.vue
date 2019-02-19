<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1" data-cy="person-toolbar">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("people.title") }}</v-toolbar-title>
        </v-flex>
        <v-flex md3>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            hide-details
            clearable
            single-line
            box
            data-cy="search"
          ></v-text-field>
        </v-flex>
        <v-flex md3>
          <div data-cy="view-dropdown">
            <v-select
              hide-details
              solo
              single-line
              :items="viewOptions"
              v-model="viewStatus"
            ></v-select>
          </div>
        </v-flex>
        <v-flex shrink justify-self-end>
          <v-btn
            class="mr-0 ml-0"
            color="primary"
            raised
            v-on:click.stop="newPerson"
            data-cy="new-person"
          >
            <v-icon left>person_add</v-icon>
            {{ $t("actions.add-person") }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-toolbar>

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :items="peopleToDisplay"
      :search="search"
      :loading="!tableLoaded"
      class="elevation-1"
      data-cy="person-table"
    >
      <template slot="items" slot-scope="props">
        <td class="text-xs-center">
          <span v-if="props.item.accountInfo">
            <span v-if="props.item.accountInfo.active">
              <v-tooltip bottom>
                <v-icon size="16" slot="activator" data-cy="account-active-icon"
                  >account_circle</v-icon
                >
                {{ $t("account.active") }}
              </v-tooltip>
            </span>

            <span v-if="!props.item.accountInfo.active">
              <v-tooltip bottom>
                <v-icon
                  size="16"
                  slot="activator"
                  data-cy="account-inactive-icon"
                  >person_outline</v-icon
                >
                {{ $t("account.inactive") }}
              </v-tooltip>
            </span>
          </span>
        </td>
        <td :data-cy="'first-name-' + props.item.id">
          {{ props.item.firstName }}
        </td>
        <td :data-cy="'last-name-' + props.item.id">
          {{ props.item.lastName }}
        </td>
        <td class="hidden-sm-and-down" :data-cy="'email-' + props.item.id">
          {{ props.item.email }}
        </td>
        <td :data-cy="'phone-' + props.item.id">{{ props.item.phone }}</td>
        <td class="text-no-wrap">
          <v-tooltip bottom>
            <v-btn
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="editPerson(props.item)"
              data-cy="edit-person"
            >
              <v-icon small>edit</v-icon>
            </v-btn>
            <span>{{ $t("actions.edit") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <v-btn
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="adminPerson(props.item)"
              data-cy="account-settings"
            >
              <v-icon small>settings</v-icon>
            </v-btn>
            <span>{{ $t("actions.tooltips.settings") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <v-btn
              v-if="props.item.active === true"
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="showConfirmDialog('deactivate', props.item)"
              data-cy="deactivate-person"
            >
              <v-icon small>archive</v-icon>
            </v-btn>
            <span>{{ $t("actions.tooltips.archive") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <v-btn
              v-if="props.item.active === false"
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="showConfirmDialog('activate', props.item)"
              data-cy="reactivate-person"
            >
              <v-icon small>undo</v-icon>
            </v-btn>
            <span>{{ $t("actions.tooltips.activate") }}</span>
          </v-tooltip>
        </td>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false" data-cy>
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog
      scrollable
      persistent
      v-model="personDialog.show"
      max-width="1000px"
    >
      <v-layout column>
        <v-card>
          <v-layout align-center justify-center row fill-height>
            <v-card-title class="headline">
              {{ $t(personDialog.title) }}
            </v-card-title>
          </v-layout>
        </v-card>
        <PersonForm
          v-bind:initialData="personDialog.person"
          v-bind:addAnotherEnabled="personDialog.addAnotherEnabled"
          v-bind:saveButtonText="personDialog.saveButtonText"
          v-bind:showAccountInfo="personDialog.showAccountInfo"
          v-bind:isAccountRequired="false"
          v-on:cancel="cancelPerson"
          v-on:saved="savePerson"
          v-on:added-another="addAnother"
        />
      </v-layout>
    </v-dialog>

    <!-- Person admin dialog -->
    <v-dialog
      scrollable
      persistent
      v-model="adminDialog.show"
      max-width="500px"
    >
      <PersonAdminForm
        v-bind:person="adminDialog.person"
        v-bind:account="adminDialog.account"
        v-bind:rolesEnabled="adminDialog.rolesEnabled"
        v-bind:rolesList="rolesList"
        v-on:addAccount="addAccount"
        v-on:updateAccount="updateAccount"
        v-on:deactivateAccount="deactivateAccount"
        v-on:reactivateAccount="reactivateAccount"
        v-on:close="closeAdmin"
      />
    </v-dialog>

    <v-dialog
      v-model="confirmDialog.show"
      max-width="350px"
      data-cy="person-table-confirmation"
    >
      <v-card>
        <v-card-text>{{ $t(confirmDialog.title) }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelAction"
            color="secondary"
            flat
            :disabled="confirmDialog.loading"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="
              confirmAction(confirmDialog.action, confirmDialog.person)
            "
            color="primary"
            raised
            :disabled="confirmDialog.loading"
            :loading="confirmDialog.loading"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import PersonForm from "./PersonForm";
import PersonAdminForm from "./AccountForm";

export default {
  name: "PersonTable",
  components: { PersonAdminForm, PersonForm },
  props: {
    peopleList: {
      type: Array,
      required: true
    },
    rolesList: {
      type: Array,
      required: true
    },
    tableLoaded: Boolean
  },
  data() {
    return {
      viewStatus: "viewActive",
      personDialog: {
        show: false,
        title: "",
        person: {},
        addAnotherEnabled: false,
        saveButtonText: "actions.save"
      },

      adminDialog: {
        show: false,
        person: {},
        account: {},
        rolesEnabled: false
      },

      confirmDialog: {
        show: false,
        action: "",
        person: {},
        title: "",
        loading: false
      },

      snackbar: {
        show: false,
        text: ""
      },

      showingArchived: false,
      selected: [],
      allPeople: [],
      activePeople: [],
      archivedPeople: [],
      search: "",
      data: {},
      translations: {}
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        {
          text: this.$t("person.account"),
          value: "person.accountInfo",
          align: "center",
          width: "3%",
          sortable: false
        },
        {
          text: this.$t("person.name.first"),
          value: "firstName",
          width: "20%"
        },
        { text: this.$t("person.name.last"), value: "lastName", width: "20%" },
        {
          text: this.$t("person.email"),
          value: "email",
          width: "20%",
          class: "hidden-sm-and-down"
        },
        { text: this.$t("person.phone"), value: "phone", width: "20%" },
        { text: this.$t("actions.header"), width: "17%", sortable: false }
      ];
    },
    viewOptions() {
      return [
        {
          text: this.$t("actions.view-active"),
          value: "viewActive",
          class: "view-active"
        },
        {
          text: this.$t("actions.view-archived"),
          value: "viewArchived",
          class: "view-archived"
        },
        { text: this.$t("actions.view-all"), value: "viewAll" }
      ];
    },
    peopleToDisplay() {
      switch (this.viewStatus) {
        case "viewActive":
          return this.activePeople;
        case "viewArchived":
          return this.archivedPeople;
        case "viewAll":
          return this.allPeople;
        default:
          return this.activePeople;
      }
    }
  },

  watch: {
    peopleList(all_people) {
      this.allPeople = all_people;
      this.activePeople = this.allPeople.filter(person => person.active);
      this.archivedPeople = this.allPeople.filter(person => !person.active);
    },
    rolesList(all_roles) {
      this.rolesList = all_roles;
    },
    tableLoaded(loading) {
      this.tableLoaded = loading;
    }
  },

  methods: {
    // ---- Person Administration

    activatePersonDialog(person = {}, isEditTitle = false) {
      this.personDialog.title = isEditTitle
        ? this.$t("person.actions.edit")
        : this.$t("person.actions.new");
      this.personDialog.showAccountInfo = !isEditTitle;
      this.personDialog.addAnotherEnabled = !isEditTitle;
      this.personDialog.person = person;
      this.personDialog.show = true;
    },

    editPerson(person) {
      this.activatePersonDialog({ ...person }, true);
    },

    newPerson() {
      this.activatePersonDialog();
    },

    cancelPerson() {
      this.personDialog.show = false;
    },

    savePerson(person) {
      let idx = this.allPeople.findIndex(p => p.id === person.id);
      if (idx !== -1) {
        Object.assign(this.allPeople[idx], person);
        this.showSnackbar(this.$t("person.messages.person-edit"));
      } else {
        this.refreshPeopleList();
        this.showSnackbar(this.$t("person.messages.person-add"));
      }
      this.personDialog.show = false;
    },

    addAnother() {
      this.refreshPeopleList();
      this.activatePersonDialog();
      this.showSnackbar(this.$t("person.messages.person-add"));
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    // ---- Account Administration

    showConfirmDialog(action, person) {
      this.confirmDialog.title = "person.messages.confirm." + action;
      this.confirmDialog.action = action;
      this.confirmDialog.person = person;
      this.confirmDialog.show = true;
    },

    confirmAction(action, person) {
      if (action == "deactivate") {
        this.deactivatePerson(person);
      } else if (action == "activate") {
        this.activatePerson(person);
      }
    },

    cancelAction() {
      this.confirmDialog.show = false;
    },

    adminPerson(person) {
      // Pass along the current person.
      this.adminDialog.person = person;
      this.rolesEnabled = false;
      // Fetch the person's account information (if any) before activating the dialog.
      this.$http
        .get(`/api/v1/people/persons/${person.id}/account`)
        .then(resp => {
          console.log("FETCHED ACCOUNT", resp);
          this.adminDialog.account = resp.data;
          this.adminDialog.show = true;
        })
        .catch(err => console.error("FAILURE", err.response));
    },
    closeAdmin() {
      this.adminDialog.show = false;
    },

    addAccount(account) {
      this.$http
        .post("/api/v1/people/accounts", account)
        .then(resp => {
          console.log("ADDED ACCOUNT", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("account.messages.added-ok"));
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    updateAccount(accountId, account) {
      this.$http
        .patch(`/api/v1/people/accounts/${accountId}`, account)
        .then(resp => {
          console.log("PATCHED ACCOUNT", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("account.messages.updated-ok"));
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    deactivateAccount(accountId) {
      this.$http
        .put(`/api/v1/people/accounts/deactivate/${accountId}`)
        .then(resp => {
          console.log("DEACTIVATED ACCOUNT", resp);
          this.showSnackbar(this.$t("person.messages.account-deactivate"));
        })
        .then(() => this.refreshPeopleList())
        .catch(err => console.error("FAILURE", err.response));
    },

    reactivateAccount(accountId) {
      this.$http
        .put(`/api/v1/people/accounts/activate/${accountId}`)
        .then(resp => {
          console.log("REACTIVATED ACCOUNT", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("person.messages.account-activate"));
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    activatePerson(person) {
      this.$http
        .put(`/api/v1/people/persons/activate/${person.id}`)
        .then(resp => {
          console.log("ACTIVATED PERSON", resp);
          this.showSnackbar(this.$t("person.messages.person-activate"));
        })
        .then(() => this.refreshPeopleList())
        .catch(err => console.error("FAILURE", err.response))
        .finally(() => {
          this.confirmDialog.loading = false;
          this.confirmDialog.show = false;
        });
    },

    deactivatePerson(person) {
      this.$http
        .put(`/api/v1/people/persons/deactivate/${person.id}`)
        .then(resp => {
          console.log("DEACTIVATED PERSON", resp);
          this.showSnackbar(this.$t("person.messages.person-deactivate"));
        })
        .then(() => this.refreshPeopleList())
        .then(() => {
          if (person.accountInfo && person.accountInfo.active) {
            this.deactivateAccount(person.accountInfo.id);
          }
        })
        .catch(err => console.error("FAILURE", err.response))
        .finally(() => {
          this.confirmDialog.loading = false;
          this.confirmDialog.show = false;
        });
    },

    refreshPeopleList() {
      this.$emit("fetchPeopleList");
    }
  }
};
</script>
