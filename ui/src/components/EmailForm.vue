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
    <v-flex class="text-xs-center">
      <v-btn
        class="ma-2"
        flat
        small
        color="primary"
        @click="showEntityTypePanel"
        :disabled="entityTypePanel.show"
      >
        {{ $t('actions.tooltips.settings') }}
      </v-btn>
    </v-flex>
    <v-flex>
      <v-expand-transition>
        <v-card
          v-if="entityTypePanel.show"
          color="teal lighten-3"
        >
          <v-radio-group v-model="radioGroup">
            <v-card-title>{{ $t('groups.members.email-reply-to') }} :   {{ replyToOtherEmail || 'null' }}</v-card-title>
            <v-card-title text color="green"></v-card-title>
            <v-radio
              :label= "$t('groups.title')"
              @click="setToChurch"
              :key='1'
              :value=homeChurchEmail
            ></v-radio>
              <v-radio
                :label= "$t('groups.details.manager')"
                @click="showManagerPanel"
                :key='2'
                :value = 'notSelected'
              ></v-radio>
              <!--  Managers dialog     -->
              <v-expand-transition>
                <v-card
                  v-if="managerPanel.show"
                >
                  <v-card-text>
                    <entity-search
                      person
                      v-model="selectedPerson"
                      :existing-entities="searchPeople"
                    />
                  </v-card-text>
                  <v-btn v-on:click="hideManagerPanel" color="light-blue" flat>{{
                    $t("actions.cancel")
                    }}</v-btn>
                  <v-btn v-on:click="setReplyTo" color="primary" flat>{{
                    $t("actions.confirm")
                    }}</v-btn>
                </v-card>
              </v-expand-transition>
            <v-radio
              :label= "$t('groups.members.default')"
              @click="setToDefault"
              :key='4'
              :value= "myEmail"
            ></v-radio>
          </v-radio-group>
          <v-card-actions>
            <v-btn small flat @click="hideEntityTypePanel">{{
              $t("actions.close")
              }}</v-btn>
            <v-spacer></v-spacer>
            <v-footer color="teal lighten-3" x-small>
              {{ $t("groups.members.email-dialog-footnote")}}
            </v-footer>
            <v-spacer></v-spacer>
            <v-btn small flat color="primary"
                   @click="saveEntityTypePanel"
            >{{
              $t("actions.save")
              }}</v-btn>
          </v-card-actions>
        </v-card>
      </v-expand-transition>
    </v-flex>
    <v-card-actions>
      <v-btn v-on:click="cancel" color="secondary" flat>{{
        $t("actions.cancel")
      }}</v-btn>
      <v-spacer>
      </v-spacer>
      <v-footer>{{replyToOtherEmail}}</v-footer>
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
import PersonDialog from "./PersonDialog";

export default {
  components: {EntitySearch },
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
    hasValidRecipients() {
      return this.email.recipients.some(recipient => recipient.email);
    },
    ...mapState(["currentAccount"]),
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
      this.email.reply_to="";
    },
    cancel() {
      this.resetEmail();
      this.syncInitialData();
      this.$emit("cancel");
    },
    sendEmail() {
      this.sendLoading = true;
      if(this.replyToOtherEmail === null){
        eventBus.$emit("error", {
          content: "groups.messages.error-sending-email"
        });
      }
      let email = {
        ...this.email,
        recipients: this.email.recipients.map(p => p.email),
        cc: this.email.cc.map(p => p.email),
        bcc: this.email.bcc.map(p => p.email),
        reply_to: this.replyToOtherEmail
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
    },
    showEntityTypePanel() {
      this.entityTypePanel.show = true;
      this.radioGroup = this.myEmail;
    },
    hideEntityTypePanel() {
      this.entityTypePanel.show = false;
      this.replyToOtherEmail = this.radioGroup;
    },
    saveEntityTypePanel(){
      this.entityTypePanel.show = false;
    },
    showManagerPanel(){
      this.managerPanel.show = true;
    },
    setReplyTo(){
      if (this.selectedPerson != null){
        this.replyToOtherEmail = this.selectedPerson.email;
        this.managerPanel.show = false;
        this.radioGroup = ' ';
      }
      else{
        eventBus.$emit("error", {
          content: "Select one email"
        });
      }
    },
    hideManagerPanel(){
      this.managerPanel.show = false;
    },
    getAllManagers(){
    },
    AllGroupManagers(){
      let groupId = this.$route.params.group;
      this.$http
        .get(`/api/v1/people/persons`)
        .then(resp => {
          this.people = resp.data;
        }).then(() => this.peronWithEmail())
      ;
    },
    peronWithEmail(){
      let i = 0
      for (let i = 0; i< this.people.length; i++){
        if ((this.people)[i].email === null){
          this.searchPeople.push((this.people)[i]);
        }
      }
    },
    setToChurch(){
      this.replyToOtherEmail = this.radioGroup;
      this.radioGroup = this.homeChurchEmail;
    },
    setToDefault(){
      this.replyToOtherEmail = this.radioGroup;
      this.radioGroup = this.myEmail;
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
        managerName: "", 
        managerEmail: "manager@xx.com",
        reply_to:""
      },
      expand:false,
      entityTypePanel: {
        show: false
      },
      managerPanel: {
        show: false
      },
      memberPanel: {
        show: false
      },
      radioGroup: 'default@email.com',
      replyToOtherEmail: ' ',
      homeChurchEmail: 'homeChurh@email.com',
      myEmail: 'default@email.com',
      managers: null,
      managerWithEmail:{},
      selectedPerson:null,
      people:[],
      searchPeople:[],
      notSelected: ' '
    };
  },
  mounted: function(){
    this.AllGroupManagers();
    this.myEmail = this.currentAccount.email;
  }
};
</script>
