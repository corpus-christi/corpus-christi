<template>
  <!-- this component emits 'sent', 'cancel', and 'error' event to signal its parent the sending status 
  The parent is responsible for showing/hiding the email dialog as appropriate -->
  <v-card>
    <v-card-title primary-title>
      <div>
        <h3 class="headline mb-0">{{ $t("groups.members.email.compose") }}</h3>
      </div>
    </v-card-title>
    <!-- TODO: Can we use a loop to render the following 3 components?
      Currently the issue is that v-model won't synchronize references
      that are returned by computed properties <2020-06-17, David Deng> -->
    <v-card-text>
      <v-select
        v-model="email.recipients"
        :label="$t('groups.members.email.to')"
        :items="initialData.recipientList"
        item-text="name"
        item-value="email"
        multiple
        chips
        deletable-chips
        hide-selected
        return-object
        :no-data-text="$t('groups.messages.no-remaining-members')"
      >
        <template v-slot:item="{ item }">
          {{ `${item.name} (${item.email})` }}
        </template>
      </v-select>
    </v-card-text>
    <v-card-text>
      <v-select
        v-model="email.cc"
        :label="$t('groups.members.email.cc')"
        :items="initialData.recipientList"
        item-text="name"
        item-value="email"
        multiple
        chips
        deletable-chips
        hide-selected
        return-object
        :no-data-text="$t('groups.messages.no-remaining-members')"
      >
        <template v-slot:item="{ item }">
          {{ `${item.name} (${item.email})` }}
        </template>
      </v-select>
    </v-card-text>
    <v-card-text>
      <v-select
        v-model="email.bcc"
        :label="$t('groups.members.email.bcc')"
        :items="initialData.recipientList"
        item-text="name"
        item-value="email"
        multiple
        chips
        deletable-chips
        hide-selected
        return-object
        :no-data-text="$t('groups.messages.no-remaining-members')"
      >
        <template v-slot:item="{ item }">
          {{ `${item.name} (${item.email})` }}
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
    <v-card-actions>
      <v-btn v-on:click="cancel" color="secondary" flat>{{
        $t("actions.cancel")
      }}</v-btn>
      <v-spacer></v-spacer>
      <v-btn
        v-on:click="sendEmail"
        :disabled="email.recipients.length == 0"
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
export default {
  props: {
    initialData: {
      /* contains the following
      'recipientList': [ { email: 'xxxx@xx.com', name: '...' }, ... ] // a list of possible recipients to be shown in selection
      'recipients: [ { email: 'xxxx@xx.com', name: '...' }, ... ] // selected recipients
      */
      type: Object,
      required: true
    }
  },
  computed: {
    selectFields() {
      return [
        {
          key: "recipients",
          model: this.email.recipients,
          label: this.$t("groups.members.email.to")
        },
        {
          key: "cc",
          model: this.email.cc,
          label: this.$t("groups.members.email.cc")
        },
        {
          key: "bcc",
          model: this.email.bcc,
          label: this.$t("groups.members.email.bcc")
        }
      ];
    },
    ...mapState(["currentAccount"])
  },
  watch: {
    "initialData.recipients": function() {
      this.syncInitialData();
    }
  },
  methods: {
    syncInitialData() {
      this.email.recipients = this.initialData.recipients;
    },
    resetEmail() {
      this.email.subject = "";
      this.email.body = "";
      this.email.recipients = [];
      this.email.cc = [];
      this.email.bcc = [];
      this.email.managerName = "";
      this.email.managerEmail = "sender@xx.com";
    },
    cancel() {
      this.resetEmail();
      this.syncInitialData();
      this.$emit("cancel");
    },
    sendEmail() {
      this.sendLoading = true;
      // transform data to compatible form
      let email = {
        ...this.email,
        recipients: this.email.recipients.map(p => p.email),
        cc: this.email.cc.map(p => p.email),
        bcc: this.email.bcc.map(p => p.email)
      };
      this.$http
        .post(`/api/v1/emails/`, email, { noErrorSnackBar: true })
        .then(() => {
          this.resetEmail();
          this.sendLoading = false;
          this.$emit("sent");
          eventBus.$emit("message", { content: "groups.messages.email-sent" });
        })
        .catch(err => {
          this.sendLoading = false;
          this.$emit("error");
          eventBus.$emit("error", {
            content: "groups.messages.error-sending-email"
          });
        });
    }
  },
  data() {
    return {
      sendLoading: false,
      email: {
        subject: "",
        body: "",
        recipients: [],
        cc: [],
        bcc: [],
        managerName: "", // TODO: use this field in the composed email later
        managerEmail: "sender@xx.com" // TODO: ask the user to choose the sender email
      }
    };
  }
};
</script>
