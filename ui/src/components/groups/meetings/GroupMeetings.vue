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
      :rows-per-page-items="rowsPerPageItem"
      :headers="headers"
      :items="visibleMeetings"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td
        >{{ props.item.description }}</td>
        <td
        >{{ props.item.startTime | formatDate }}</td>
        <td
        >{{ props.item.stopTime | formatDate }}</td>
        <td
        >{{ props.item.attendances }}</td>
        <td
        >{{ props.item.address.address}}</td>
        <td>
          <template v-if="props.item.active">
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="confirmArchive(props.item)"
                data-cy="archive"
              >
                <v-icon small>archive</v-icon>
              </v-btn>
              <span>{{ $t("actions.tooltips.archive") }}</span>
            </v-tooltip>
          </template>

          <template v-if="props.item.active">
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="showAttendance(props.item)"
                data-cy="viewAttendance"
              >
                <v-icon small>people</v-icon>
              </v-btn>
              <span>{{ $t("actions.tooltips.view-attendance") }}</span>
            </v-tooltip>
          </template>

          <template v-else>
            <v-tooltip bottom v-if="!props.item.active">
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="unarchive(props.item)"
                :loading="props.item.id < 0"
                data-cy="unarchive"
              >
                <v-icon small>undo</v-icon>
              </v-btn>
              <span>{{ $t("actions.tooltips.activate") }}</span>
            </v-tooltip>
          </template>
        </td>
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
            flat
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
            flat
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
            <h2>
              {{ $t("events.attendance") }}
            </h2>
          </div>
          <v-spacer></v-spacer>
          <v-btn class="mx-2" fab small color="primary">
            <v-icon
              v-on:click="addParticipants"
            >add</v-icon>
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
            :items="attendance_people_list"
            class="elevation-1"
          >
            <template v-slot:items="props">
              <td>{{ props.item }}</td>
              <td>
                <v-btn
                  icon
                  outline
                  small
                  color="primary"
                  slot="activator"
                  v-on:click="confirmArchiveAttendance(props)"
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
            flat
            data-cy="cancel-archive"
          >{{ $t("actions.cancel") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Add People from a Meeting Dialog -->
    <v-dialog v-model="addPeronToMeeting.show" max-width="350px">
      <v-card>
        <v-card-title primary-title>
          <div>
            <h3 class="headline mb-0">
              {{ $t("person.actions.add-participant") }}
            </h3>
          </div>
        </v-card-title>
        <v-card-actions>
          <v-btn
            v-on:click="cancelNewAttendanceDialog"
            color="secondary"
            flat
            data-cy=""
          >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
<!--          :disabled="addParticipantDialog.newParticipants.length === 0"-->
<!--          :loading="addParticipantDialog.loading"-->

          <v-btn
            color="primary"
            raised
            data-cy="confirm-participant"
            v-on:click="addParticipants"
          >{{ $t("actions.add-participant") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Add/Edit Meeting Dialog -->
    <v-dialog v-model="meetingDialog.show" persistent max-width="500px">
      <meeting-form
        :edit-mode="false"
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
            flat
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
      <v-btn flat @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import CustomForm from "../../CustomForm";
import EntitySearch from "../../EntitySearch";

export default {
  components: { "meeting-form": CustomForm, EntitySearch },
  name: "GroupMeetings",
  data() {
    return {
      rowsPerPageItem: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 }
      ],
      tableLoading: false,
      search: "",
      meetingDialog: {
        show: false,
        meeting: null,
        saveLoading: false
      },
      meetings: [],
      deleteDialog: {
        show: false,
        participantId: -1,
        loading: false
      },
      addAttendanceDialog: {
        show: false,
        newParticipants: [],
        loading: false
      },
      archiveDialog: {
        show: false,
        meetingId: -1,
        loading: false
      },
      archiveAttendanceDialog:{
        show: false,
        personId:-1,
        loading: false
      },
      addPeronToMeeting:{
        show:false,
        personId:-1
      },
      snackbar: {
        show: false,
        text: ""
      },
      meeting:{
        active:''
      },
      attendanceDialog:{
        show: false
      },
      viewStatus: "viewActive",
      attendances_number: [],
      attendance_list:[],
      attendance_people_list:[],
      currentMeetings:[],
      ViewingMeetingId: null
    };
  },

  computed: {
    viewOptions() {
      return [
        { text: this.$t("actions.view-active"), value: "viewActive" },
        { text: this.$t("actions.view-archived"), value: "viewArchived" },
        { text: this.$t("actions.view-all"), value: "viewAll" }
      ];
    },
    visibleMeetings() {
      let list = this.meetings;

      if (this.viewStatus === "viewActive") {
        return list.filter(ev => ev.active);
      } else if (this.viewStatus === "viewArchived") {
        return list.filter(ev => !ev.active);
      } else {
        return list;
      }
    },
    headers() {
      return [
        {
          text: this.$t("groups.description"),
          value: "description",
          width: "20%"
        },
        {
          text: this.$t("events.start-time"),
          value: "startTime",
          width: "20%"
        },
        {
          text: this.$t("events.stop-time"),
          value: "stopTime",
          width: "22.5%"
        },
        { text: this.$t("events.attendance"), value: "attendance" },
        { text: this.$t("events.event-location"), value: "location_name" },
        { text: this.$t("actions.header"), sortable: false }
      ];
    },
    attendance_headers(){
      return [
        {
          text: "Attendance",
          value: "attendance",
          width: "20%"
        },
        {
          text: "Action",
          value: "attendance.action",
          width: "20%"
        }
      ];
    }
  },

  methods: {
    PeopleFromMeetingDialog(){
      this.addPeronToMeeting.show = true;
    },

    cancelNewAttendanceDialog(){
      this.addPeronToMeeting.show = false;
    },

    activateEditMeetingDialog() {
      this.meetingDialog.editMode = true;
      this.activateMeetingDialog();
    },

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
          this.showSnackbar(this.$t("groups.messages.meeting-added"));
          this.meetingDialog.saveLoading = false;
          this.meetingDialog.show = false;
          this.getMeetings();
        })
        .catch(err => {
          console.log(err);
          this.meetingDialog.saveLoading = false;
          this.showSnackbar(this.$t("groups.messages.error-adding-meeting"));
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

    addParticipants() {
      this.addAttendanceDialog.loading = true;
      let promises = [];
      for (let person of this.addAttendanceDialog.newParticipants) {
        const idx = this.attendance_list.findIndex(
          at_pe => at_pe.person.personId === person.id
        );
        if (idx === -1) {
          promises.push(this.addMeetingParticipant(person.id));
        }
      }
      Promise.all(promises)
        .then(() => {
          this.showSnackbar(this.$t("groups.messages.members-added"));
          this.refreshAttendance(this.ViewingMeetingId);
          this.addAttendanceDialog.loading = false;
          this.addAttendanceDialog.show = false;
          this.addAttendanceDialog.newParticipants = [];
          this.getMembers();
        })
        .catch(err => {
          console.log(err);
          this.addAttendanceDialog.loading = false;
          this.showSnackbar(this.$t("groups.messages.error-adding-members"));
        });
    },

    addMeetingParticipant(id) {
      const groupId = this.$route.params.group;
      for (const person of this.attendance_people_list) {
        if (id == person.personId) {
          return true;
        }
      }
      return this.$http.put(`/api/v1/groups/meetings/${ this.ViewingMeetingId }/attendances/${ id }`);
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
        joined: "2018-12-25"
      });
    },

    confirmDelete(event) {
      this.activateDeleteDialog(event.person_id);
    },

    deleteParticipant() {
      this.deleteDialog.loading = true;
      const participantId = this.deleteDialog.participantId;
      const idx = this.people.findIndex(ev => ev.person.id === participantId);
      const id = this.$route.params.event;
      this.$http
        .delete(`/api/v1/events/${id}/participants/${participantId}`)
        .then(() => {
          this.deleteDialog.loading = false;
          this.deleteDialog.show = false;
          this.people.splice(idx, 1);
          this.showSnackbar(this.$t("events.participants.removed"));
        })
        .catch(err => {
          console.log(err);
          this.deleteDialog.loading = false;
          this.deleteDialog.show = false;
          this.showSnackbar(this.$t("events.participants.error-removing"));
        });
    },
    cancelDelete() {
      this.deleteDialog.show = false;
    },
    activateDeleteDialog(participantId) {
      this.deleteDialog.show = true;
      this.deleteDialog.participantId = participantId;
    },
    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
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
      this.activateArchiveAttendanceDialog(this.attendance_list[event.item]);
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
      const idx = this.meetings.findIndex(ev => ev.id === meetingId);
      this.meeting['active'] = 'false';
      this.$http
        .patch(`/api/v1/groups/meetings/${meetingId}`, this.meeting)
        .then(resp => {
          console.log("ARCHIVE", resp);
          this.meetings[idx].active = false;
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("groups.messages.meeting-archived"));
        })
        .catch(err => {
          console.error("ARCHIVE FALURE", err.response);
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("groups.messages.error-archiving-meeting"));
        });
    },

    archiveMeetingAttendance(){
      this.archiveAttendanceDialog.loading = true;
      const attendanceID = this.archiveAttendanceDialog.personId;
      const groupId = this.$route.params.group;
      this.$http
        .delete(`/api/v1/groups/meetings/${ this.ViewingMeetingId }/attendances/${ attendanceID }`)
          .then(resp => {
            this.refreshAttendance(this.ViewingMeetingId);
            console.log("ARCHIVE", resp);
            this.archiveAttendanceDialog.loading = false;
            this.archiveAttendanceDialog.show = false;
            this.showSnackbar(this.$t("groups.messages.attendance-archived"));
          })
          .catch(err => {
            console.error("ARCHIVE FALURE", err.response);
            this.archiveAttendanceDialog.loading = false;
            this.archiveAttendanceDialog.show = false;
            this.showSnackbar(this.$t("groups.messages.error-archiving-attendance"));
          });
    },

    unarchive(meeting) {
      const idx = this.meetings.findIndex(ev => ev.id === meeting.id);
      const meetingId = meeting.id;
      meeting.id *= -1;
      this.meeting['active'] = 'true';
      this.$http
        .patch(`/api/v1/groups/meetings/${meetingId}`, this.meeting)
        .then(resp => {
          console.log("UNARCHIVED", resp);
          Object.assign(this.meetings[idx], resp.data);
          this.showSnackbar(this.$t("groups.messages.meeting-unarchived"));
        })
        .catch(err => {
          console.error("UNARCHIVE FALURE", err.response);
          this.showSnackbar(
            this.$t("groups.messages.error-unarchiving-meeting")
          );
        });
    },

    getMeetings() {
      this.tableLoading = true;
      const id = this.$route.params.group;
      this.$http
        .get(`/api/v1/groups/meetings?where=group_id:${id}`)
        .then(resp => {
          if (!resp.data.msg) {
            let meetingId = []
            for (let i = 0; i < resp.data.length; i++){
              meetingId.push(resp.data[i].id);
            }
            for (let i = 0; i < resp.data.length; i++){
              this.$http
                .get(`/api/v1/groups/meetings/${ meetingId[i] }/attendances`)
                .then(resp1 => {
                  resp.data[i].attendances = resp1.data.length;
                });
            }
            this.meetings = resp.data;
          }
          this.tableLoading = false;
        });
    },
    showAttendance(event){
      const meetingId = event.id;
      this.ViewingMeetingId = event.id;
      this.$http
        .get(`/api/v1/groups/meetings/${meetingId}/attendances`)
        .then(resp => {
          for (let i = 0; i < resp.data.length; i++){
            this.attendance_list[resp.data[i].person.firstName] = resp.data[i].personId;
            this.attendance_people_list = resp.data.map(p=> p.person.firstName);
          }
        });
      this.attendanceDialog.show = true;
    },

    refreshAttendance(id){
      this.$http
        .get(`/api/v1/groups/meetings/${id}/attendances`)
        .then(resp => {
          for (let i = 0; i < resp.data.length; i++){
            this.attendance_list[resp.data[i].person.firstName] = resp.data[i].personId;
            this.attendance_people_list = resp.data.map(p=> p.person.firstName);
          }
        });
      this.attendanceDialog.show = true;
    },

    cancelShowAttendance(){
      this.attendanceDialog.show = false;
      this.getMeetings();
    }
  },

  mounted: function() {
    this.getMeetings();
  }
};
</script>
