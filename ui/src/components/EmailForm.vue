<template>
  <!-- this component emits 'sent', 'cancel', and 'error' event to signal its parent the sending status 
  The parent is responsible for showing/hiding the email dialog as appropriate -->
  <v-card>
    <v-card-title primary-title>
      <div>
        <h3 class="headline mb-0">{{ $t("groups.members.email.compose") }}</h3>
      </div>
    </v-card-title>
    <v-card-text>
      <v-select
        v-model="email.recipients"
        :label="$t('groups.members.email.to')"
        :items="initialData.recipientList"
        item-text="person.firstName"
        item-value="person.email"
        multiple
        chips
        deletable-chips
        hide-selected
        return-object
        :no-data-text="$t('groups.messages.no-remaining-members')"
      >
        <template v-slot:item="{ item }">
          {{ `${item.person.firstName + " " + item.person.lastName} (${item.person.email})` }}
        </template>
      </v-select>
    </v-card-text>
    <v-card-text>
      <v-text-field
        :label="$t('groups.members.email.subject')"
        v-model="email.subject"
      >
      </v-text-field>
    </v-card-text>
    <v-card-text>
      <v-textarea :label="$t('groups.members.email.body')" v-model="email.body">
      </v-textarea>
    </v-card-text>
    <v-flex class="text-xs-center">
      <v-btn
        class="ma-2"
        text
        small
        color="primary"
        @click="showEntityTypePanel"
        :disabled="entityTypePanel.show"
      >
        {{ $t("actions.tooltips.settings") }}
      </v-btn>
    </v-flex>
    <v-flex>
      <!-- Expansion -->
      <v-expand-transition>
        <v-card v-if="entityTypePanel.show" color="teal lighten-3">
          <v-radio-group v-model="radioGroup">
            <v-card-title text color="green"></v-card-title>
            <v-radio
              :label="$t('groups.title')"
              @click="setToChurch"
              :key="1"
              :value="homeChurchEmail"
            ></v-radio>
            <v-radio
              :label="$t('groups.details.manager')"
              @click="showManagerPanel"
              :key="2"
              :value="notSelected"
            ></v-radio>
            <!--  Managers dialog     -->
            <v-expand-transition>
              <v-card v-if="managerPanel.show">
                <v-card-text>
                  <entity-search
                    multiple
                    person
                    v-model="selectedPerson"
                    :existing-entities="searchPeople"
                  />
                </v-card-text>
                <v-btn v-on:click="hideManagerPanel" color="light-blue" text>{{
                  $t("actions.cancel")
                }}</v-btn>
              </v-card>
            </v-expand-transition>
            <v-radio
              :label="$t('groups.members.default')"
              :key="4"
              :value="myEmail"
            ></v-radio>
          </v-radio-group>
          <v-card-actions>
            <v-btn small text @click="hideEntityTypePanel">{{
              $t("actions.close")
            }}</v-btn>
            <v-spacer></v-spacer>
            <v-footer color="teal lighten-3" x-small>
              {{ $t("groups.members.email-dialog-footnote") }}
            </v-footer>
            <v-spacer></v-spacer>
            <v-btn small text color="primary" @click="hideEntityTypePanel">{{
              $t("actions.save")
            }}</v-btn>
          </v-card-actions>
        </v-card>
      </v-expand-transition>
    </v-flex>
    <v-card-actions>
      <v-btn v-on:click="cancel" color="secondary" text>{{
        $t("actions.cancel")
      }}</v-btn>
      <v-spacer> </v-spacer>
      <v-spacer />
      <v-btn
        v-on:click="sendEmail"
        :disabled="!hasValidRecipients"
        color="primary"
        raised
        :loading="sendLoading"
        data-cy="confirm-email"
        >{{ $t("groups.members.email.send") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>
<script>
import { mapState } from "vuex";
import { eventBus } from "../plugins/event-bus.js";
import EntitySearch from "./EntitySearch";

export default {
  components: { EntitySearch },
  props: {
    initialData: {
      /* contains the following
      'recipientList': [ { email: 'xxxx@xx.com', name: '...' }, ... ] // a list of possible recipients to be shown in selection
      'recipients: [ { email: 'xxxx@xx.com', name: '...' }, ... ] // selected recipients
      */
      type: Object,
      required: true,
      default: function() {
        return {}
      },
      
    },
  },
  computed: {
    hasValidRecipients() {
      return this.email.recipients.some((recipient) => recipient.person.email);
    },
    ...mapState(["currentAccount"]),
  },
  watch: {
    "initialData.recipients": function () {
      this.syncInitialData();
    },

  },
  methods: {
    
    syncInitialData() {
      this.email.recipients = this.initialData.recipients;
      console.log("SYNCING", this.email);
    },
    resetEmail() {
      this.email.subject = "";
      this.email.body = "";
      this.email.recipients = [];
      //this.email.managerName = ""
      this.email.managerEmail = "corpus.christi.test@gmail.com";
    },
    cancel() {
      this.resetEmail();
      this.syncInitialData();
      this.$emit("cancel");
    },
    sendEmail() {
      this.sendLoading = true;
      console.log("pre-EMAIL", this.email);
      let email = {
        ...this.email,
        recipients: this.email.recipients.map((p) => p.person.email)
      };
      console.log("SENDING", email);
      this.$http
        .post(`/api/v1/emails/`, email, { noErrorSnackBar: true })
        .then(() => {
          this.resetEmail();
          this.sendLoading = false;
          this.$emit("sent");
          eventBus.$emit("message", { content: "groups.messages.email-sent" });
        })
        .catch((err) => {
          console.error("EMAIL ERROR", err);
          this.sendLoading = false;
          this.$emit("error");
          console.log(err);
          eventBus.$emit("error", {
            content: "groups.messages.error-sending-email",
          });
        });
    },
    showEntityTypePanel() {
      this.entityTypePanel.show = true;
      this.radioGroup = this.myEmail;
    },
    hideEntityTypePanel() {
      this.entityTypePanel.show = false;
    },
    showManagerPanel() {
      this.managerPanel.show = true;
    },
    hideManagerPanel() {
      this.managerPanel.show = false;
    },
    AllGroupManagers() {
      this.$http
        .get(`/api/v1/people/persons`)
        .then((resp) => {
          this.people = resp.data;
        })
        .then(() => this.peronWithEmail());
    },
    peronWithEmail() {
      for (let i = 0; i < this.people.length; i++) {
        if (this.people[i].email === null) {
          this.searchPeople.push(this.people[i]);
        }
      }
    },
    setToChurch() {
      this.radioGroup = this.homeChurchEmail;
    },
    setToDefault() {
      this.radioGroup = this.myEmail;
    },
  },
  data() {
    return {
      sendLoading: false,
      email: {
        subject: "",
        body: "",
        recipients: [],
        managerName: "",
        managerEmail: "corpus.christi.test@gmail.com",
      },
      expand: false,
      entityTypePanel: {
        show: false,
      },
      managerPanel: {
        show: false,
      },
      memberPanel: {
        show: false,
      },
      notSelected: " ",
      radioGroup: "default@email.com",
      homeChurchEmail: "homeChurh@email.com",
      myEmail: "qiang_wang@taylor.edu",
      managers: null,
      managerWithEmail: {},
      selectedPerson: null,
      people: [],
      searchPeople: [],
    };
  },
  mounted: function () {
    this.AllGroupManagers();
    this.myEmail = this.currentAccount.email;
    this.email.managerName = this.currentAccount.firstName + " " + this.currentAccount.lastName;
  },
};
</script>
