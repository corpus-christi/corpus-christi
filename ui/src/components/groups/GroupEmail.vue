<template>
    <div>
      <!-- Email dialog -->
      <v-dialog v-model="emailDialog.show" max-width="700px">
        <v-card>
          <v-card-title primary-title>
            <div>
              <h3 class="headline mb-0">
                {{ $t("groups.members.email.compose") }}
              </h3>
            </div>
          </v-card-title>
          <v-card-text>
            <v-select
              v-model="email.recipients"
              :label="$t('groups.members.email.to')"
              :items="parsedMembers"
              multiple
              chips
              deletable-chips
              hide-selected
              :no-data-text="$t('groups.messages.no-remaining-members')"
            >
            </v-select>
          </v-card-text>
          <v-card-text>
            <v-select
              v-model="email.cc"
              :label="$t('groups.members.email.cc')"
              :items="parsedMembers"
              multiple
              chips
              deletable-chips
              hide-selected
              :no-data-text="$t('groups.messages.no-remaining-members')"
            >
            </v-select>
          </v-card-text>
          <v-card-text>
            <v-select
              v-model="email.bcc"
              :label="$t('groups.members.email.bcc')"
              :items="parsedMembers"
              multiple
              chips
              deletable-chips
              :no-data-text="$t('groups.messages.no-remaining-members')"
            >
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
            <v-textarea
              :label="$t('groups.members.email.body')"
              v-model="email.body"
            >
            </v-textarea>
          </v-card-text>
          <v-card-actions>
            <v-btn
              v-on:click="toggleEmailDialog"
              color="secondary"
              flat
              data-cy=""
            >{{ $t("actions.cancel") }}</v-btn
            >
            <v-spacer></v-spacer>
            <v-btn
              v-on:click="sendEmail"
              :disabled="email.recipients.length == 0"
              color="primary"
              raised
              :loading="sendEmail.loading"
              data-cy="confirm-email"
            >{{ $t("groups.members.email.send") }}</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
</template>

<script>
    export default {
        name: "GroupEmail",
        date(){
          return{
            email: {
              subject: "",
              body: "",
              recipients: [],
              cc: [],
              bcc: [],
              managerName: "",
              managerEmail: ""
            },
            emailDialog: {
              show: false,
              loading: false
            }
          }
        },
      methods:{
        toggleEmailDialog() {
          if (this.selected.length > 0) {
            this.email.recipients = this.getEmailRecipients();
            this.emailDialog.show = !this.emailDialog.show;
          } else this.showSnackbar("No valid email addresses are selected");
        },
        sendEmail() {
          this.email['managerEmail'] = this.currentAccount.email;
          console.log("----",this.email);
          this.$http
            .post(`/api/v1/emails/`, this.email)
            .then(() => {
              this.toggleEmailDialog();
              this.selected = [];
              this.email.subject = "";
              this.email.body = "";
              this.email.cc = "";
              this.email.bcc = "";
              this.showSnackbar(this.$t("groups.messages.email-sent"));
            })
            .catch(err => {
              this.showSnackbar(this.$t("groups.messages.error-no-manager-email"));
              console.log(this.email);
              console.log(err);
            });
        }
      }
    }
</script>

<style scoped>

</style>
