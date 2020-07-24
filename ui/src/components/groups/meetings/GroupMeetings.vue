<template>
  <div>
    <v-toolbar>
      <v-flex md3>
        <v-toolbar-title>{{ $t("groups.meetings.title") }}</v-toolbar-title>
      </v-flex>
      <v-spacer></v-spacer>
      <v-flex md2>
        <v-text-field
          v-model="search"
          append-icon="search"
          v-bind:label="$t('actions.search')"
          single-line
          hide-details
        ></v-text-field>
      </v-flex>
      <v-spacer></v-spacer>
      <v-flex md1>
        <v-select
          hide-details
          solo
          single-line
          :items="viewOptions"
          v-model="viewStatus"
          data-cy="view-status-select"
        >
        </v-select>
      </v-flex>

      <v-spacer></v-spacer>
      <v-flex>
        <v-btn
          color="primary"
          raised
          v-on:click="activateCreateMeetingDialog"
          data-cy="add-meeting"
        >
          <v-icon dark left>add</v-icon>
          {{ $t("groups.meetings.add-meeting") }}
        </v-btn>
      </v-flex>
    </v-toolbar>
    <v-data-table
      :items-per-page-options="rowsPerPageItem"
      :headers="headers"
      :items="visibleMeetings"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
      must-sort
      :options.sync="options"
    >
      <template v-slot:item="props">
        <tr>
          <td
            class="hover-hand"
            v-on:click="
                $router.push({
                  name: 'meeting-members',
                  params: { meeting: props.item.attendances[0].meetingId },
                })
              "
          >{{ props.item.description }}
          </td>
          <td
            class="hover-hand"
            v-on:click="
                $router.push({
                  name: 'meeting-members',
                  params: { meeting: props.item.attendances[0].meetingId },
                })
              "
          >{{ props.item.startTime | formatDate }}
          </td>
          <td
            class="hover-hand"
            v-on:click="
                $router.push({
                  name: 'meeting-members',
                  params: { meeting: props.item.attendances[0].meetingId },
                })
              "
          >{{ props.item.stopTime | formatDate }}
          </td>
          <td
            class="hover-hand"
            v-on:click="
                $router.push({
                  name: 'meeting-members',
                  params: { meeting: props.item.attendances[0].meetingId },
                })
              "
          >{{ props.item.attendances.length }}
          </td>
          <td
            class="hover-hand"
            v-on:click="
                $router.push({
                  name: 'meeting-members',
                  params: { meeting: props.item.attendances[0].meetingId },
                })
              "
          >{{ props.item.address.address }}
          </td>
          <td>
            <template v-if="props.item.active">
              <v-tooltip bottom>
                <template  v-slot:activator="{ on }">
                  <v-btn
                    v-on="on"
                    icon
                    outlined
                    small
                    color="primary"
                    slot="activator"
                    v-on:click="confirmArchive(props.item)"
                    data-cy="archive"
                  >
                    <v-icon small>archive</v-icon>
                  </v-btn>
                </template>
                <span>{{ $t("actions.tooltips.archive") }}</span>
              </v-tooltip>
              <v-tooltip bottom>
                <template v-slot:activator="{ on }">
                  <v-btn
                    v-on="on"
                    icon
                    outlined
                    small
                    color="primary"
                    slot="activator"
                    :to="{
                      name: 'meeting-details',
                      params: { meeting: props.item.id },
                    }"
                    data-cy="viewAttendance"
                  >
                    <v-icon small>people</v-icon>
                  </v-btn>
                </template>
                <span>{{ $t("actions.tooltips.take-attendance") }} </span>
              </v-tooltip>
            </template>
            <template v-else>
              <v-tooltip bottom v-if="!props.item.active">
                <template v-slot:activator="{ on }">
                <v-btn
                  v-on="on"
                  icon
                  outlined
                  small
                  color="primary"
                  slot="activator"
                  v-on:click="unarchive(props.item)"
                  :loading="props.item.id < 0"
                  data-cy="unarchive"
                >
                  <v-icon small>undo</v-icon>
                </v-btn>
                </template>
                <span>{{ $t("actions.tooltips.activate") }}</span>
              </v-tooltip>
            </template>
        </td>
        </tr>
      </template>
    </v-data-table>

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{
          $t("groups.messages.confirm-meeting-archive")
        }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelArchive"
            color="secondary"
            text
            data-cy="cancel-archive"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="archiveMeeting"
            color="primary"
            raised
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Archive Attendance dialog -->
    <v-dialog v-model="archiveAttendanceDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{
          $t("groups.messages.confirm-attendance-archive")
        }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelAttendanceArchive"
            color="secondary"
            text
            data-cy="cancel-archive"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="archiveMeetingAttendance"
            color="primary"
            raised
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Attendance dialog -->
    <v-dialog v-model="attendanceDialog.show" max-width="400px">
      <v-card>
        <v-card-title primary-title>
          <div>
            <h2>{{ $t("events.attendance") }}</h2>
          </div>
          <v-spacer></v-spacer>
          <v-btn class="mx-2" fab small color="primary">
            <v-icon v-on:click="addAttendances">add</v-icon>
          </v-btn>
          <v-card-text>
            <entity-search
              multiple
              person
              v-model="addAttendanceDialog.newParticipants"
            />
          </v-card-text>
        </v-card-title>
        <v-data-table
          :headers="attendance_headers"
          :items="attendanceDialog.attendances"
          class="elevation-1"
        >
          <template v-slot:items="props">
            <td>{{ props.item.person.firstName }}</td>
            <td>
              <v-btn
                icon
                outlined
                small
                color="primary"
                slot="activator"
                v-on:click="archiveMeetingAttendance"
                data-cy="archive"
              >
                <v-icon small>archive</v-icon>
              </v-btn>
            </td>
          </template>
        </v-data-table>
        <v-card-actions>
          <v-btn
            v-on:click="cancelShowAttendance"
            color="secondary"
            text
            data-cy="cancel-archive"
            >{{ $t("actions.cancel") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Add/Edit Meeting Dialog -->
    <v-dialog v-model="meetingDialog.show" persistent max-width="500px">
      <meeting-form
        :edit-mode="false"
        create-text="groups.meetings.add-meeting"
        :initial-data="meetingDialog.meeting"
        :save-loading="meetingDialog.saveLoading"
        descriptionLabel="Description Label"
        locationLabel="Location Label"
        startDateTimeField
        endDateTimeField
        v-on:cancel="cancelMeetingDialog"
        v-on:save="saveMeeting"
      ></meeting-form>
    </v-dialog>

    <!-- Delete dialog -->
    <v-dialog v-model="deleteDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{
          $t("events.participants.confirm-remove")
        }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDelete"
            color="secondary"
            text
            data-cy="cancel-delete"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deleteParticipant"
            color="primary"
            raised
            :loading="deleteDialog.loading"
            data-cy="confirm-delete"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn text @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import CustomForm from "../../CustomForm";
import EntitySearch from "../../EntitySearch";
import { eventBus } from "../../../plugins/event-bus.js";
export default {
  components: { "meeting-form": CustomForm, EntitySearch },
  name: "GroupMeetings",
  data() {
    return {
      options: {
        sortBy: ["activeMembers.length"], //default sorted column
        sortDesc: [true],
        itemsPerPage: 10,
        page: 1,
      },
      rowsPerPageItem: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 },
      ],
      tableLoading: false,
      search: "",
      meetingDialog: {
        show: false,
        meeting: null,
        saveLoading: false,
      },
      meetings: [],
      deleteDialog: {
        show: false,
        participantId: -1,
        loading: false,
      },
      addAttendanceDialog: {
        show: false,
        newParticipants: [],
        loading: false,
      },
      archiveDialog: {
        show: false,
        meetingId: -1,
        loading: false,
      },
      archiveAttendanceDialog: {
        show: false,
        personId: -1,
        loading: false,
      },
      addPeronToMeeting: {
        show: false,
        personId: -1,
      },
      snackbar: {
        show: false,
        text: "",
      },
      meeting: {
        active: "",
      },
      attendanceDialog: {
        show: false,
        attendances: [],
      },
      viewStatus: "viewActive",
      attendance_list: [],
      attendance_people_list: [],
      ViewingMeetingId: null,
    };
  },

  computed: {
    meetingDescriptions() {
      return this.meetings.map((m) => m.description);
    },
    viewOptions() {
      return [
        { text: this.$t("actions.view-active"), value: "viewActive" },
        { text: this.$t("actions.view-archived"), value: "viewArchived" },
        { text: this.$t("actions.view-all"), value: "viewAll" },
      ];
    },
    visibleMeetings() {
      let list = this.meetings;

      if (this.viewStatus === "viewActive") {
        return list.filter((ev) => ev.active);
      } else if (this.viewStatus === "viewArchived") {
        return list.filter((ev) => !ev.active);
      } else {
        return list;
      }
    },
    headers() {
      return [
        {
          text: this.$t("groups.description"),
          value: "description",
          width: "20%",
        },
        {
          text: this.$t("events.start-time"),
          value: "startTime",
          width: "20%",
        },
        {
          text: this.$t("events.stop-time"),
          value: "stopTime",
          width: "22.5%",
        },
        { text: this.$t("events.attendance"), value: "attendance" },
        { text: this.$t("events.event-location"), value: "location_name" },
        { text: this.$t("actions.header"), sortable: false },
      ];
    },
    attendance_headers() {
      return [
        {
          text: "Attendance",
          value: "attendance",
          width: "20%",
        },
        {
          text: "Action",
          value: "attendance.action",
          width: "20%",
        },
      ];
    },
  },

  methods: {
    activateCreateMeetingDialog() {
      this.meetingDialog.editMode = false;
      this.activateMeetingDialog();
    },

    activateMeetingDialog() {
      this.meetingDialog.show = true;
    },

    cancelMeetingDialog() {
      this.meetingDialog.show = false;
    },

    saveMeeting(meeting) {
      this.meetingDialog.saveLoading = true;

      meeting.groupId = this.$route.params.group;
      meeting.addressId = meeting.location.address.id;
      meeting.startTime = meeting.start;
      meeting.stopTime = meeting.end;

      delete meeting.location;
      delete meeting.start;
      delete meeting.end;

      const existingMeeting = this.meetings.find(({ id }) => id === meeting.id);
      if (typeof existingMeeting === "undefined") {
        this.createMeeting(meeting);
      } else {
        this.updateMeeting(meeting);
      }
    },
    createMeeting(meeting) {
      return this.$http
        .post(`/api/v1/groups/meetings`, meeting)
        .then(() => {
          eventBus.$emit("message", {
            content: this.$t("groups.messages.meeting-added"),
          });
          this.meetingDialog.saveLoading = false;
          this.meetingDialog.show = false;
          this.getMeetings();
        })
        .catch((err) => {
          console.log(err);
          this.meetingDialog.saveLoading = false;
          eventBus.$emit("error", {
            content: this.$t("groups.messages.error-adding-meeting"),
          });
        });
    },

    getDisplayLocation(location, length = 20) {
      if (location && location.description) {
        let name = location.description;
        if (name && name.length && name.length > 0) {
          if (name.length > length) {
            return `${name.substring(0, length - 3)}...`;
          }
          return name;
        }
      }
      return name;
    },

    addAttendances() {
      this.addAttendanceDialog.loading = true;
      let promises = [];
      for (let person of this.addAttendanceDialog.newParticipants) {
        const idx = this.attendance_list.findIndex(
          (at_pe) => at_pe.person.personId === person.id
        );
        if (idx === -1) {
          promises.push(this.addMeetingParticipant(person.id));
        }
      }
      Promise.all(promises)
        .then(() => {
          eventBus.$emit("message", {
            content: this.$t("groups.messages.members-added"),
          });
          this.addAttendanceDialog.loading = false;
          this.addAttendanceDialog.show = false;
          this.addAttendanceDialog.newParticipants = [];
          this.refreshAttendance();
        })
        .catch((err) => {
          console.log(err);
          this.addAttendanceDialog.loading = false;
          eventBus.$emit("error", {
            content: this.$t("groups.messages.error-adding-members"),
          });
        });
    },

    addMeetingParticipant(id) {
      for (const person of this.attendance_people_list) {
        if (id == person.personId) {
          return true;
        }
      }
      return this.$http.put(
        `/api/v1/groups/meetings/${this.ViewingMeetingId}/attendances/${id}`
      );
    },

    addParticipant(id) {
      const groupId = this.$route.params.group;
      for (const meeting of this.meetings) {
        if (id == meeting.person.id) {
          return true;
        }
      }
      return this.$http.post(`/api/v1/groups/meetings`, {
        group_id: groupId,
        person_id: id,
        joined: "2018-12-25",
      });
    },

    confirmDelete(event) {
      this.activateDeleteDialog(event.person_id);
    },

    deleteParticipant() {
      this.deleteDialog.loading = true;
      const participantId = this.deleteDialog.participantId;
      const idx = this.people.findIndex((ev) => ev.person.id === participantId);
      const id = this.$route.params.event;
      this.$http
        .delete(`/api/v1/events/${id}/participants/${participantId}`)
        .then(() => {
          this.deleteDialog.loading = false;
          this.deleteDialog.show = false;
          this.people.splice(idx, 1);
          eventBus.$emit("message", {
            content: this.$t("events.participants.removed"),
          });
        })
        .catch((err) => {
          console.log(err);
          this.deleteDialog.loading = false;
          this.deleteDialog.show = false;
          eventBus.$emit("error", {
            content: this.$t("events.participants.error-removing"),
          });
        });
    },
    cancelDelete() {
      this.deleteDialog.show = false;
    },
    activateDeleteDialog(participantId) {
      this.deleteDialog.show = true;
      this.deleteDialog.participantId = participantId;
    },

    activateArchiveDialog(meetingId) {
      this.archiveDialog.show = true;
      this.archiveDialog.meetingId = meetingId;
    },

    activateArchiveAttendanceDialog(personID) {
      this.archiveAttendanceDialog.show = true;
      this.archiveAttendanceDialog.personId = personID;
    },

    confirmArchive(event) {
      this.activateArchiveDialog(event.id);
    },

    confirmArchiveAttendance(event) {
      this.activateArchiveAttendanceDialog(event.item.person.id);
    },

    cancelArchive() {
      this.archiveDialog.show = false;
    },
    cancelAttendanceArchive() {
      this.archiveAttendanceDialog.show = false;
    },

    archiveMeeting() {
      this.archiveDialog.loading = true;
      const meetingId = this.archiveDialog.meetingId;
      const idx = this.meetings.findIndex((ev) => ev.id === meetingId);
      this.meeting["active"] = "false";
      this.$http
        .patch(`/api/v1/groups/meetings/${meetingId}`, this.meeting)
        .then((resp) => {
          console.log("ARCHIVE", resp);
          this.meetings[idx].active = false;
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          eventBus.$emit("message", {
            content: this.$t("groups.messages.meeting-archived"),
          });
        })
        .catch((err) => {
          console.error("ARCHIVE FALURE", err.response);
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          eventBus.$emit("error", {
            content: this.$t("groups.messages.error-archiving-meeting"),
          });
        });
    },

    archiveMeetingAttendance() {
      this.archiveAttendanceDialog.loading = true;
      const attendanceID = this.archiveAttendanceDialog.personId;
      this.$http
        .delete(
          `/api/v1/groups/meetings/${this.ViewingMeetingId}/attendances/${attendanceID}`
        )
        .then((resp) => {
          this.refreshAttendance();
          console.log("ARCHIVE", resp);
          this.archiveAttendanceDialog.loading = false;
          this.archiveAttendanceDialog.show = false;
          eventBus.$emit("message", {
            content: this.$t("groups.messages.attendance-archived"),
          });
        })
        .catch((err) => {
          console.error("ARCHIVE FALURE", err.response);
          this.archiveAttendanceDialog.loading = false;
          this.archiveAttendanceDialog.show = false;
          eventBus.$emit("error", {
            content: this.$t("groups.messages.error-archiving-attendance"),
          });
        });
    },

    unarchive(meeting) {
      const idx = this.meetings.findIndex((ev) => ev.id === meeting.id);
      const meetingId = meeting.id;
      meeting.id *= -1;
      this.meeting["active"] = "true";
      this.$http
        .patch(`/api/v1/groups/meetings/${meetingId}`, this.meeting)
        .then((resp) => {
          console.log("UNARCHIVED", resp);
          Object.assign(this.meetings[idx], resp.data);
          eventBus.$emit("message", {
            content: this.$t("groups.messages.meeting-unarchived"),
          });
        })
        .catch((err) => {
          console.error("UNARCHIVE FALURE", err.response);
          eventBus.$emit("error", {
            content: this.$t("groups.messages.error-unarchiving-meeting"),
          });
        });
    },

    getMeetings() {
      this.tableLoading = true;
      const id = this.$route.params.group;
      this.$http
        .get(`/api/v1/groups/meetings?where=group_id:${id}`)
        .then((resp) => {
          if (!resp.data.msg) {
            let meetingId = [];
            for (let i = 0; i < resp.data.length; i++) {
              meetingId.push(resp.data[i].id);
            }
            for (let i = 0; i < resp.data.length; i++) {
              this.$http
                .get(`/api/v1/groups/meetings/${meetingId[i]}/attendances`)
                .then((resp1) => {
                  resp.data[i].attendances = resp1.data;
                });
            }
            this.meetings = resp.data;
          }
          this.tableLoading = false;
        });
    },

    showAttendance(meeting) {
      const meetingId = meeting.id;
      this.ViewingMeetingId = meeting.id;
      this.attendanceDialog.show = true;
      this.attendanceDialog.attendances = this.meetings.find(
        (m) => m.id == meetingId
      ).attendances;
    },

    refreshAttendance() {
      this.attendanceDialog.attendances = [];
      this.tableLoading = true;
      const groupId = this.$route.params.group;
      this.$http
        .get(`/api/v1/groups/meetings?where=group_id:${groupId}`)
        .then((resp) => {
          let meetingId = [];
          for (let i = 0; i < resp.data.length; i++) {
            meetingId.push(resp.data[i].id);
          }
          for (let i = 0; i < resp.data.length; i++) {
            this.$http
              .get(`/api/v1/groups/meetings/${meetingId[i]}/attendances`)
              .then((resp1) => {
                resp.data[i].attendances = resp1.data;
              });
          }
          this.meetings = resp.data;
          this.tableLoading = false;
        })
        .then(() => {
          this.updateData();
        });
    },

    updateData() {
      const meetingId = this.ViewingMeetingId;
      this.attendanceDialog.show = true;
      this.attendanceDialog.attendances = this.meetings.find(
        (m) => m.id == meetingId
      ).attendances;
    },

    cancelShowAttendance() {
      this.attendanceDialog.show = false;
      this.getMeetings();
    },
  },

  mounted: function () {
    this.getMeetings();
  },
};
</script>
