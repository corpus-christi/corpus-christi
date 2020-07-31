<template>
  <div>
    <v-container style="max-width: 600px;">
      <v-timeline clipped align-top id="time-line-container">
        <v-timeline-item
          fill-dot
          class="white--text mb-12"
          color="orange"
          large
        >
          <template v-slot:icon>
            <span
              v-text="currentAccount.firstName[0] + currentAccount.lastName[0]"
            >
            </span>
          </template>
        </v-timeline-item>
        <v-timeline-item
          v-for="event in timeline"
          :key="event.id"
          class="mb-4"
          :color="defineColor(event) ? 'green lighten-1' : 'red'"
          small
          :left="true"
        >
          <v-card>
            <v-card-title class="orange lighten-2" v-model="admin">
              {{ $t("groups.membership-history.note") }}
              <v-spacer />
              <v-tooltip bottom>
                <template v-slot:activator="{ on }" v-if="ifAdmin">
                  <v-btn
                    color="orange lighten-2"
                    small
                    v-on="on"
                    v-on:click="clearNote(event, event.id)"
                    ><v-icon>clear</v-icon></v-btn
                  >
                </template>
                <span>{{ $t("groups.membership-history.clear-note") }}</span>
              </v-tooltip>
              <v-tooltip bottom v-if="ifAdmin">
                <template v-slot:activator="{ on }">
                  <v-btn
                    color="orange lighten-2"
                    small
                    v-on="on"
                    v-on:click="showDialog(event)"
                    ><v-icon>note_add</v-icon></v-btn
                  >
                </template>
                <span>{{ $t("groups.membership-history.change-note") }}</span>
              </v-tooltip>
            </v-card-title>
            <v-card-text v-text="event.note"></v-card-text>
          </v-card>
          <v-row justify="space-between" slot="opposite">
            <v-col
              v-if="event.text.slice(-1) === '-'"
              cols="7"
              v-text="event.text + $t('groups.membership-history.left')"
            ></v-col>
            <v-col
              v-else
              cols="7"
              v-text="event.text + $t('groups.membership-history.joined')"
            ></v-col>
            <v-col
              class="text-right"
              cols="5"
              v-text="event.time.slice(0, -6)"
            ></v-col>
          </v-row>
        </v-timeline-item>
      </v-timeline>
      <!-- Note dialog-->
      <v-dialog v-model="addNoteDialog" max-width="344">
        <v-card>
          <v-card-text>
            <v-text-field label="Note" v-model="addedNote"></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn
                  color="orange lighten-2"
                  small
                  v-on="on"
                  v-on:click="hideDialog"
                  ><v-icon>cancel</v-icon></v-btn
                >
              </template>
              <span>{{ $t("groups.membership-history.cancel") }}</span>
            </v-tooltip>
            <v-spacer />
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn
                  color="orange lighten-2"
                  small
                  v-on="on"
                  v-on:click="changeNote()"
                  >{{ $t("groups.membership-history.submit") }}</v-btn
                >
              </template>
            </v-tooltip>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  name: "GroupMembershipHistory",
  components: {},
  data() {
    return {
      events: [],
      input: null,
      nonce: 0,
      history: null,
      personalInfo: {},
      singleTime: [],
      timeMap: {},
      content: null,
      notes: "",
      right: false,
      left: false,
      historyId: null,
      newNote: null,
      addNoteDialog: false,
      addedNote: null,
      editingNoteId: null,
      admin: null,
    };
  },
  computed: {
    ifAdmin() {
      if (this.currentAccount.roles.includes("role.group-admin")) {
        return true;
      } else return false;
    },
    timeline() {
      return this.events;
    },
    ...mapState(["currentAccount"]),
    ...mapState(["currentLocale"]),
    id() {
      return parseInt(this.$route.params.group);
    },
    locale(text) {
      return text.text;
    },
  },
  methods: {
    hideDialog() {
      this.addNoteDialog = false;
    },
    showDialog(event) {
      this.editingNoteId = event.recordId;
      this.addNoteDialog = true;
    },
    clearNote(event) {
      let payload = { note: "" };
      return this.$http
        .patch(`api/v1/groups/member-histories/${event.recordId}`, payload)
        .then((resp) => {
          console.log(resp.status);
          window.location.reload();
        });
    },
    changeNote() {
      console.log(this.addedNote);
      let payload = { note: this.addedNote };
      this.addNoteDialog = false;
      return this.$http
        .patch(`api/v1/groups/member-histories/${this.editingNoteId}`, payload)
        .then((resp) => {
          console.log(resp.status);
          window.location.reload();
        });
    },
    defineColor(event) {
      if (event.text.slice(-1) === "-") {
        return false;
      } else return true;
    },
    comment() {
      const time = new Date().toTimeString();
      this.events.push({
        id: this.nonce++,
        text: this.input,
        time: time.replace(/:\d{2}\sGMT-\d{4}\s\((.*)\)/, (match, contents) => {
          return ` ${contents
            .split(" ")
            .map((v) => v.charAt(0))
            .join("")}`;
        }),
      });

      this.input = null;
    },
    fetchHistory() {
      return this.$http.get("api/v1/groups/member-histories").then((resp) => {
        this.history = resp.data.filter(
          (person_history) => person_history.groupId === this.id
        );
        if (this.notes.length === 0) {
          for (let record of this.history) {
            if (record.note != null) {
              this.notes = this.notes.concat(
                "( ",
                record.person.firstName,
                " ",
                record.person.lastName,
                ": ",
                record.note,
                ")  "
              );
            }
          }
        }

        for (let i = 0; i < this.history.length; i++) {
          this.singleTime.push(this.history[i]);
          this.singleTime.push(this.history[i]);
        }
        for (let i = 0; i < this.singleTime.length; i++) {
          if (i % 2 === 0) {
            if (!(this.singleTime[i].time in this.timeMap)) {
              this.timeMap[this.singleTime[i].time] = {
                join: [],
                left: [],
              };
            }
            if (this.singleTime[i].time in this.timeMap) {
              this.timeMap[this.singleTime[i].time].join.push(
                this.singleTime[i]
              );
            }
          } else {
            if (!(this.singleTime[i].time in this.timeMap)) {
              this.timeMap[this.singleTime[i].time] = {
                join: [],
                left: [],
              };
            }
            if (this.singleTime[i].time in this.timeMap) {
              this.timeMap[this.singleTime[i].time].left.push(
                this.singleTime[i]
              );
            }
          }
        }
        let order = Object.keys(this.timeMap).sort();
        for (let i = 0; i < order.length; i++) {
          let key = order[i];
          for (let j = 0; j < this.timeMap[key].join.length; j++) {
            this.events.push({
              id: this.nonce++,
              text:
                this.timeMap[key].join[j].person.firstName +
                " " +
                this.timeMap[key].join[j].person.lastName +
                " +",
              time: this.timeMap[key].join[j].time,
              note: this.timeMap[key].join[j].note,
              recordId: this.timeMap[key].join[j].id,
            });
          }
          for (let j = 0; j < this.timeMap[key].left.length; j++) {
            this.events.push({
              id: this.nonce++,
              text:
                this.timeMap[key].left[j].person.firstName +
                " " +
                this.timeMap[key].left[j].person.lastName +
                " -",
              time: this.timeMap[key].left[j].time,
              note: this.timeMap[key].left[j].note,
              recordId: this.timeMap[key].join[j].id,
            });
          }
        }
      });
    },
    parser(time) {
      let year = parseInt(time.slice(0, 4), 10);
      let month = parseInt(time.slice(5, 7), 10);
      let day = parseInt(time.slice(8), 10);
      return [year, month, day];
    },
  },
  mounted() {
    this.fetchHistory();
  },
};
</script>

<style scoped></style>
