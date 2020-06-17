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
        <td>{{ props.item.description }}</td>
        <td>{{ props.item.startTime | formatDate }}</td>
        <td>{{ props.item.stopTime | formatDate }}</td>
        <td>{{ props.item.address.address}}</td>
<!--           <td>{{ getDisplayLocation(props.item.location) }}123</td>-->
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
            v-on:click="archiveGroup"
            color="primary"
            raised
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ $t("actions.confirm") }}</v-btn
          >
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
export default {
  components: { "meeting-form": CustomForm },
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
      archiveDialog: {
        show: false,
        meetingId: -1,
        loading: false
      },
      snackbar: {
        show: false,
        text: ""
      },
      meeting:{
        active:''
      },
      viewStatus: "viewActive",
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
        { text: this.$t("events.event-location"), value: "location_name" },
        { text: this.$t("actions.header"), sortable: false }
      ];
    }
  },

  methods: {
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

    confirmArchive(event) {
      this.activateArchiveDialog(event.id);
    },

    cancelArchive() {
      this.archiveDialog.show = false;
    },

    archiveGroup() {
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

    unarchive(meeting) {
      const idx = this.meetings.findIndex(ev => ev.id === meeting.id);
      const meetingId = meeting.id;
      meeting.id *= -1; // to show loading spinner
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
            this.meetings = resp.data;
          }
          this.tableLoading = false;
        });
    }
  },

  mounted: function() {
    this.getMeetings();
  }
};
</script>
