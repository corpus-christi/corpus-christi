<template>
  <div>
    <!-- Header -->
    <v-toolbar data-cy="person-toolbar">
      <v-row align="center" justify="space-between">
        <v-col cols="2">
          <v-toolbar-title>{{ $t("people.title") }}</v-toolbar-title>
        </v-col>
        <v-col cols="4">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            hide-details
            clearable
            single-line
            filled
            data-cy="search"
          />
        </v-col>
        <v-col cols="2">
          <div data-cy="view-dropdown">
            <v-select
              hide-details
              solo
              single-line
              :items="viewOptions"
              v-model="viewStatus"
            />
          </div>
        </v-col>
        <v-col cols="2">
          <v-btn color="primary" v-on:click="newPerson" data-cy="new-person">
            <v-icon left>person_add</v-icon>
            {{ $t("actions.add-person") }}
          </v-btn>
        </v-col>
      </v-row>
    </v-toolbar>

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :items="peopleToDisplay"
      :search="search"
      :loading="!tableLoaded"
      class="elevation-1"
      data-cy="person-table"
      hide-default-footer
      @page-count="pageCount = $event"
      :page.sync="page"
    >
      <template v-slot:item="{ item }">
        <tr>
          <td :data-cy="'first-name-' + item.id">
            {{ item.firstName }}
          </td>
          <td :data-cy="'last-name-' + item.id">
            {{ item.lastName }}
          </td>
          <td class="hidden-sm-and-down" :data-cy="'email-' + item.id">
            {{ item.email }}
          </td>
          <td :data-cy="'phone-' + item.id">{{ item.phone }}</td>
          <td class="text-no-wrap">
            <ActionIconButton
              icon-name="edit"
              v-bind:tooltipText="$t('actions.edit')"
              v-on:click="editPerson(item)"
            />

            <ActionIconButton
              icon-name="settings"
              v-bind:tooltipText="$t('actions.tooltips.settings')"
              v-on:click="adminPerson(item)"
            />

            <ActionIconButton
              v-if="item.active === true"
              iconName="archive"
              v-bind:tooltipText="$t('actions.tooltips.archive')"
              v-on:click="showConfirmDialog('deactivate', item)"
            />

            <ActionIconButton
              v-if="item.active === false"
              iconName="undo"
              v-bind:tooltip-text="$t('actions.tooltips.activate')"
              v-on:click="showConfirmDialog('activate', item)"
            />
          </td>
        </tr>
      </template>
    </v-data-table>
    <div class="text-center pt-2">
      <v-pagination v-model="page" :length="pageCount"></v-pagination>
    </div>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn text @click="snackbar.show = false" data-cy>
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <person-dialog
      v-on:snack="showSnackbar"
      v-on:cancel="cancelPerson"
      v-on:refreshPeople="refreshPeopleList"
      v-bind:dialog-state="dialogState"
      v-bind:all-people="allPeople"
      v-bind:person="person"
    />

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
            text
            :disabled="confirmDialog.loading"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
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
import PersonDialog from "../PersonDialog";
import PersonAdminForm from "./AccountForm";
import ActionIconButton from "@/components/people/ActionIconButton";

export default {
  name: "PersonTable",
  components: { ActionIconButton, PersonDialog, PersonAdminForm },
  props: {
    peopleList: {
      type: Array,
      required: true,
    },
    rolesList: {
      type: Array,
      required: true,
    },
    tableLoaded: Boolean,
  },
  data() {
    return {
      viewStatus: "viewActive",

      page: 1,
      pageCount: 0,

      adminDialog: {
        show: false,
        person: {},
        rolesEnabled: false,
      },

      confirmDialog: {
        show: false,
        action: "",
        person: {},
        title: "",
        loading: false,
      },

      snackbar: {
        show: false,
        text: "",
      },

      showingArchived: false,
      selected: [],
      dialogState: "",
      person: {},
      allPeople: [],
      activePeople: [],
      archivedPeople: [],
      search: "",
      data: {},
      translations: {},
    };
  },

  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        {
          text: this.$t("person.name.first"),
          value: "firstName",
          width: "20%",
        },
        { text: this.$t("person.name.last"), value: "lastName", width: "20%" },
        {
          text: this.$t("person.email"),
          value: "email",
          width: "20%",
          class: "hidden-sm-and-down",
        },
        { text: this.$t("person.phone"), value: "phone", width: "20%" },
        { text: this.$t("actions.header"), width: "20%", sortable: false },
      ];
    },

    viewOptions() {
      return [
        {
          text: this.$t("actions.view-active"),
          value: "viewActive",
          class: "view-active",
        },
        {
          text: this.$t("actions.view-archived"),
          value: "viewArchived",
          class: "view-archived",
        },
        { text: this.$t("actions.view-all"), value: "viewAll" },
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
    },
  },

  watch: {
    peopleList(all_people) {
      this.allPeople = all_people;
      this.activePeople = this.allPeople.filter((person) => person.active);
      this.archivedPeople = this.allPeople.filter((person) => !person.active);
    },

    // It seems like these watches are updating themselves when they update themselves.
    // Not necessary?
    // rolesList(all_roles) {
    //   this.rolesList = all_roles;
    // },
    //
    // tableLoaded(loading) {
    //   this.tableLoaded = loading;
    // },
  },

  methods: {
    // ---- Person Administration

    editPerson(person) {
      this.dialogState = "edit";
      this.person = person;
    },

    newPerson() {
      this.dialogState = "new";
    },

    cancelPerson() {
      this.dialogState = "";
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
      if (action === "deactivate") {
        this.deactivatePerson(person);
      } else if (action === "activate") {
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
        .get(`/api/v1/people/persons/${person.id}`)
        .then((resp) => {
          console.log("FETCHED ACCOUNT", resp);
          this.adminDialog.account = resp.data;
          this.adminDialog.show = true;
        })
        .catch((err) => console.error("FAILURE", err.response));
    },
    closeAdmin() {
      this.adminDialog.show = false;
    },

    addAccount(account) {
      this.$http
        .post("/api/v1/people/accounts", account)
        .then((resp) => {
          console.log("ADDED ACCOUNT", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("account.messages.added-ok"));
        })
        .catch((err) => console.error("FAILURE", err.response));
    },

    updateAccount(accountId, account) {
      this.$http
        .patch(`/api/v1/people/accounts/${accountId}`, account)
        .then((resp) => {
          console.log("PATCHED ACCOUNT", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("account.messages.updated-ok"));
        })
        .catch((err) => console.error("FAILURE", err.response));
    },

    deactivateAccount(accountId) {
      this.$http
        .put(`/api/v1/people/accounts/deactivate/${accountId}`)
        .then((resp) => {
          console.log("DEACTIVATED ACCOUNT", resp);
          this.showSnackbar(this.$t("person.messages.account-deactivate"));
        })
        .then(() => this.refreshPeopleList())
        .catch((err) => console.error("FAILURE", err.response));
    },

    reactivateAccount(accountId) {
      this.$http
        .put(`/api/v1/people/accounts/activate/${accountId}`)
        .then((resp) => {
          console.log("REACTIVATED ACCOUNT", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("person.messages.account-activate"));
        })
        .catch((err) => console.error("FAILURE", err.response));
    },

    activatePerson(person) {
      this.$http
        .put(`/api/v1/people/persons/activate/${person.id}`)
        .then((resp) => {
          console.log("ACTIVATED PERSON", resp);
          this.showSnackbar(this.$t("person.messages.person-activate"));
        })
        .then(() => this.refreshPeopleList())
        .catch((err) => console.error("FAILURE", err.response))
        .finally(() => {
          this.confirmDialog.loading = false;
          this.confirmDialog.show = false;
        });
    },

    deactivatePerson(person) {
      this.$http
        .put(`/api/v1/people/persons/deactivate/${person.id}`)
        .then((resp) => {
          console.log("DEACTIVATED PERSON", resp);
          this.showSnackbar(this.$t("person.messages.person-deactivate"));
        })
        .then(() => this.refreshPeopleList())
        .then(() => {
          if (person.accountInfo && person.accountInfo.active) {
            this.deactivateAccount(person.accountInfo.id);
          }
        })
        .catch((err) => console.error("FAILURE", err.response))
        .finally(() => {
          this.confirmDialog.loading = false;
          this.confirmDialog.show = false;
        });
    },

    refreshPeopleList() {
      this.$emit("fetchPeopleList");
    },
  },
};
</script>
