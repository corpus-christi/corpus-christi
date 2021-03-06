<template>
  <div>
    <v-toolbar class="pa-1">
      <v-row no-gutters align="center" justify="space-between" fill-height>
        <v-col md="3">
          <v-toolbar-title>{{
            $t("groups.members.title-visitor")
          }}</v-toolbar-title>
        </v-col>
      </v-row>
      <v-col md="2"> </v-col>
      <v-spacer />
      <template v-if="isOverseer === true || ifAdmin">
        <v-col>
          <v-btn color="primary" raised v-on:click.stop="newVisitor">
            <v-icon dark left>person_add</v-icon>
            {{ $t("person.actions.add-visitor") }}
          </v-btn>
        </v-col>
        <v-col>
          <v-btn
            class="ma-2"
            outlined
            small
            fab
            color="primary"
            v-on:click="activateNewVisitorDialog"
          >
            <v-icon>search</v-icon>
          </v-btn>
        </v-col>
      </template>
    </v-toolbar>
    <v-data-table
      v-model="selected"
      class="elevation-1"
      :headers="headers"
      :items="visitors"
      item-key="id"
      :search="search"
    >
      <template v-slot:item="props">
        <tr>
          <td>{{ props.item.firstName }}</td>
          <td>{{ props.item.lastName }}</td>
          <template v-if="isOverseer === true || ifAdmin">
            <td>
              <v-tooltip bottom>
                <template v-slot:activator="{ on }">
                  <v-btn
                    icon
                    outlined
                    small
                    color="primary"
                    slot="activator"
                    data-cy="archive"
                    v-on:click="removeVisitor(props.item)"
                    v-on="on"
                  >
                    <v-icon small>delete_outline</v-icon>
                  </v-btn>
                </template>
                <span>{{ $t("actions.tooltips.remove") }}</span>
              </v-tooltip>
            </td>
          </template>
        </tr>
      </template>
    </v-data-table>

    <!-- Add visitor Dialog -->
    <v-dialog v-model="addVisitorDialog.show" max-width="350px">
      <v-card>
        <v-card-title primary-title>
          <div>
            <h3 class="headline mb-0">
              {{ $t("person.actions.add-visitor") }}
            </h3>
          </div>
        </v-card-title>
        <v-card-text>
          <entity-search
            multiple
            person
            v-model="addVisitorDialog.newVisitors"
            :existing-entities="attendance"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelNewVisitorDialog"
            color="secondary"
            text
            data-cy=""
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="addNewVisitor"
            color="primary"
            raised
            data-cy="confirm-participant"
            >{{ $t("person.actions.add-visitor") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- New/Edit dialog -->
    <person-dialog
      @snack="showSnackbar"
      @cancel="cancelPerson"
      :person="person"
      :dialog-state="dialogState"
      :all-people="allPeople"
    />
  </div>
</template>

<script>
import { eventBus } from "../../plugins/event-bus";
import PersonDialog from "../PersonDialog";
import EntitySearch from "../EntitySearch";
import { mapState } from "vuex";
import {
  convertToGroupMap,
  isOverseer,
  getParticipantById,
} from "../../models/GroupHierarchyNode.ts";
export default {
  name: "GroupMeetingVisitor",
  components: { PersonDialog, EntitySearch },
  data() {
    return {
      addVisitorDialog: {
        show: false,
        newVisitors: [],
        loading: false,
      },
      selected: [],
      visitors: [],
      allAttendance: [],
      attendance: [],
      search: "",
      allPeople: [],
      dialogState: "",
      currentGroupId: null,
      person: {},
      people: [],
      snackbar: {
        show: false,
        text: "",
      },
    };
  },

  methods: {
    openVisitorDialog() {
      this.activateNewVisitorDialog();
    },
    activateNewVisitorDialog() {
      this.addVisitorDialog.show = true;
    },
    cancelNewVisitorDialog() {
      this.addVisitorDialog.show = false;
    },
    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },
    cancelPerson() {
      this.dialogState = "";
    },
    newVisitor() {
      this.dialogState = "new";
    },
    fetchMeeting() {
      const meetingId = this.$route.params.meeting;
      this.$http
        .get(`/api/v1/groups/meetings/${meetingId}`)
        .then((resp) => {
          this.currentGroupId = resp.data.groupId;
        })
        .then(() => this.getAllGroupMember());
    },
    getAllGroupMember() {
      let allMember = [];
      this.$http
        .get(`/api/v1/groups/groups/${this.currentGroupId}/members`)
        .then((resp) => {
          this.attendance = resp.data.map((e) => e.person);
          for (let person of this.attendance) {
            allMember.push(person.id);
          }
          for (let person of this.allAttendance) {
            if (allMember.includes(person.personId) === false) {
              this.visitors.push({
                firstName: person.firstName,
                lastName: person.lastName,
                id: person.personId,
              });
            }
          }
        });
    },
    refreshAllGroupMember() {
      this.attendance = [];
      this.allAttendance = [];
      this.visitors = [];
      let allMember = [];
      this.$http
        .get(`/api/v1/groups/groups/${this.currentGroupId}/members`)
        .then((resp) => {
          this.attendance = resp.data.map((e) => e.person);
          for (let person of this.attendance) {
            allMember.push(person.id);
          }
          for (let person of this.allAttendance) {
            if (allMember.includes(person.personId) === false) {
              this.visitors.push({
                firstName: person.firstName,
                lastName: person.lastName,
                id: person.personId,
              });
            }
          }
        });
    },
    allMeetingAttendance() {
      const meetingId = this.$route.params.meeting;
      this.$http
        .get(`/api/v1/groups/meetings/${meetingId}/attendances`)
        .then((resp) => {
          this.recordAttendance = resp.data;

          for (let person of this.recordAttendance) {
            this.allAttendance.push({
              firstName: person.person.firstName,
              lastName: person.person.lastName,
              personId: person.person.id,
            });
          }
        });
    },
    refreshAllMeetingAttendance() {
      this.allAttendance = [];
      const meetingId = this.$route.params.meeting;
      this.$http
        .get(`/api/v1/groups/meetings/${meetingId}/attendances`)
        .then((resp) => {
          this.recordAttendance = resp.data;

          for (let person of this.recordAttendance) {
            this.allAttendance.push({
              firstName: person.person.firstName,
              lastName: person.person.lastName,
              personId: person.person.id,
            });
          }
        });
    },
    readAllPeople() {
      this.$http.get(`/api/v1/people/persons`).then((resp) => {
        this.people = resp.data;
      });
    },
    refreshFetchMeeting() {
      //working
      const meetingId = this.$route.params.meeting;
      this.$http
        .get(`/api/v1/groups/meetings/${meetingId}`)
        .then((resp) => {
          this.currentGroupId = resp.data.groupId;
        })
        .then(() => this.refreshAllMeetingAttendance())
        .then(() => this.refreshAllGroupMember());
    },
    addNewVisitor() {
      let meetingId = this.$route.params.meeting;
      let currentVisitorId = [];
      for (let person of this.visitors) {
        currentVisitorId.push(person.id);
      }
      for (let person of this.addVisitorDialog.newVisitors) {
        if (currentVisitorId.includes(person.id) === false) {
          let personId = person.id;
          this.$http
            .put(`/api/v1/groups/meetings/${meetingId}/attendances/${personId}`)
            .then(() => {
              eventBus.$emit("message", {
                content: "groups.messages.participant-added",
              });
            })
            .catch((err) => {
              console.log(err);
              eventBus.$emit("error", {
                content: "events.participants.error-adding",
              });
            })
            .then(() => this.refreshFetchMeeting());
        } else {
          eventBus.$emit("error", {
            content: "events.participants.error-adding",
          });
        }
      }
    },
    removeVisitor(person) {
      let meetingId = this.$route.params.meeting;
      this.$http
        .delete(`/api/v1/groups/meetings/${meetingId}/attendances/${person.id}`)
        .then(() => {
          eventBus.$emit("message", {
            content: "groups.messages.visitor-remove",
          });
        })
        .then(() => this.refreshFetchMeeting());
    },
    isOverseer() {
      let currentParticipant = getParticipantById(
        this.currentAccount.id,
        this.groupMap
      );
      return currentParticipant
        ? isOverseer(currentParticipant, this.currentGroupId)
        : false;
    },
  },

  computed: {
    headers() {
      return [
        {
          text: this.$t("person.name.first"),
          value: "person.firstName",
          width: "20%",
        },
        {
          text: this.$t("person.name.last"),
          value: "person.lastName",
          width: "20%",
        },
        {
          text: this.$t("actions.header"),
          sortable: false,
        },
      ];
    },
    ...mapState(["currentAccount"]),
    groupMap() {
      return convertToGroupMap(this.allGroups);
    },
    id() {
      return this.currentGroupId;
    },
    ifAdmin() {
      if (
        this.currentAccount.roles.includes("role.group-admin") ||
        this.currentAccount.roles.includes("role.group-leader")
      ) {
        return true;
      } else return false;
    },
  },
  mounted: function () {
    this.fetchMeeting();
    this.allMeetingAttendance();
    this.readAllPeople();
  },
};
</script>
<style scoped></style>
