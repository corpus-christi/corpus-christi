<template>
  <div>
    <v-toolbar class="pa-1">
      <v-row no-gutters align="center" justify="space-between" fill-height>
        <v-col md="3">
          <v-toolbar-title>{{
            $t("actions.tooltips.take-attendance")
          }}</v-toolbar-title>
        </v-col>
        <v-col md="2">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            single-line
            hide-details
          />
        </v-col>
      </v-row>
    </v-toolbar>
    <v-data-table
      v-model="selected"
      :headers="headers"
      class="elevation-1"
      :items="listMember"
      item-key="personId"
      :search="search"
      show-select
    >
      <template v-slot:item="props">
        <tr>
          <td><v-checkbox v-model="props.selected" primary hide-details /></td>
          <td>{{ props.item.firstName }}</td>
          <td>{{ props.item.lastName }}</td>
        </tr>
      </template>
    </v-data-table>
    <v-col md="3">
      <v-btn
        class="ma-2"
        outlined
        color="green"
        v-on:click="submitSelectedPeople"
        >{{ $t("error-report.actions.submit") }}</v-btn
      >
    </v-col>
  </div>
</template>

<script>
import { eventBus } from "../../plugins/event-bus";

export default {
  name: "GroupMeetingMember",
  data() {
    return {
      currentGroupId: null,
      meetings: [],
      participants: [],
      attendances: [],
      search: "",
      selected: [],
      listMember: [],
      recordAttendance: [],
      markList: [],
    };
  },
  methods: {
    parseMembers() {
      this.attendance.map((e) => {
        if (e.id) {
          this.listMember.push({
            firstName: e.firstName,
            lastName: e.lastName,
            personId: e.id,
          });
        }
      });
    },
    fetchMeeting() {
      this.tableLoading = true;
      const meetingId = this.$route.params.meeting;
      this.$http
        .get(`/api/v1/groups/meetings/${meetingId}`)
        .then((resp) => {
          this.currentGroupId = resp.data.groupId;
        })
        .then(() => this.getAllGroupMember());
    },
    getAllGroupMember() {
      this.$http
        .get(`/api/v1/groups/groups/${this.currentGroupId}/members`)
        .then((resp) => {
          this.attendance = resp.data.map((e) => e.person);
          this.parseMembers();
        });
    },
    allMeetingAttendance() {
      const meetingId = this.$route.params.meeting;
      this.$http
        .get(`/api/v1/groups/meetings/${meetingId}/attendances`)
        .then((resp) => {
          this.recordAttendance = resp.data;
          for (let person of this.recordAttendance) {
            this.selected.push({
              firstName: person.person.firstName,
              lastName: person.person.lastName,
              personId: person.person.id,
            });
          }
        });
    },

    submitSelectedPeople() {
      const meetingId = this.$route.params.meeting;
      let currentStore = [];
      let newAttendance = [];
      let selectedId = [];
      let missingId = [];
      for (let person of this.recordAttendance) {
        currentStore.push(person.person.id);
      }

      for (let i = 0; i < this.selected.length; i++) {
        if (currentStore.includes(this.selected[i].personId) === false) {
          newAttendance.push(this.selected[i].personId);
        }
      }
      for (let i = 0; i < newAttendance.length; i++) {
        this.$http
          .patch(
            `/api/v1/groups/meetings/${meetingId}/attendances/${newAttendance[i]}`
          )
          .then(() => {
            eventBus.$emit("message", {
              content: this.$t("groups.messages.participant-added"),
            });
            this.allMeetingAttendance();
          })
          .catch((err) => {
            console.log(err);
            eventBus.$emit("error", {
              content: this.$t("events.participants.error-adding"),
            });
          });
      }
      if (this.selected.length < currentStore.length) {
        for (let i = 0; i < this.selected.length; i++) {
          selectedId.push(this.selected[i].personId);
        }
        for (let i = 0; i < this.listMember.length; i++) {
          if (selectedId.includes(this.listMember[i].personId) === false) {
            missingId.push(this.listMember[i].personId);
          }
        }
        for (let i = 0; i < missingId.length; i++) {
          if (currentStore.includes(missingId[i]) === true) {
            this.$http
              .delete(
                `/api/v1/groups/meetings/${meetingId}/attendances/${missingId[i]}`
              )
              .then(() => {
                eventBus.$emit("message", {
                  content: this.$t("groups.messages.participant-added"),
                });
                this.allMeetingAttendance();
              })
              .catch((err) => {
                console.log(err);
                eventBus.$emit("error", {
                  content: this.$t("events.participants.error-adding"),
                });
              });
          }
        }
      }
    },
  },
  computed: {
    headers() {
      return [
        {
          text: this.$t("person.name.first"),
          value: "firstName",
          width: "20%",
        },
        {
          text: this.$t("person.name.last"),
          value: "lastName",
          width: "20%",
        },
      ];
    },
  },
  mounted: function () {
    this.fetchMeeting();
    this.allMeetingAttendance();
  },
};
</script>
<style scoped></style>
