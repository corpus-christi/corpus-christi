<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>{{ $t("courses.schedule") }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="$t('actions.search')"
        single-line
        hide-details
      ></v-text-field>
      <v-spacer></v-spacer>
      <v-btn color="primary" @click.stop="newClassMeeting">
        <v-icon dark left>event</v-icon>
        {{ $t("courses.add-meeting") }}
      </v-btn>
    </v-toolbar>
    <v-data-table
      :headers="headers"
      :items="meetings"
      :search="search"
      :loading="loading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.displayDate }}</td>
        <td>{{ props.item.location.description }}</td>
        <td>{{ props.item.teacher.compositeName }}</td>
        <td>
          <v-layout align-center justify-end>
            <v-tooltip bottom>
              <v-btn
                flat
                icon
                outline
                small
                color="primary"
                slot="activator"
                @click="editClassMeeting(props.item)"
              >
                <v-icon small>edit</v-icon>
              </v-btn>
              <span>{{ $t("actions.edit") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <v-btn
                flat
                icon
                outline
                small
                color="primary"
                slot="activator"
                @click="openAttendance(props.item)"
              >
                <v-icon small>assignment_ind</v-icon>
              </v-btn>
              <span>{{ $t("courses.class-attendance") }}</span>
            </v-tooltip>
          </v-layout>
        </td>
      </template>
    </v-data-table>

    <!-- New/Edit dialog -->
    <v-dialog
      persistent
      scrollable
      v-model="classMeetingDialog.show"
      max-width="500px"
    >
      <ClassMeetingForm
        v-bind:editMode="classMeetingDialog.editMode"
        v-bind:initialData="classMeetingDialog.classMeeting"
        v-bind:offeringId="offeringId"
        v-on:cancel="cancelClassMeeting"
        v-on:save="saveClassMeeting"
      />
    </v-dialog>

    <!-- Attendance dialog -->
    <v-dialog
      persistent
      scrollable
      v-model="attendanceDialog.show"
      max-width="500px"
    >
      <ClassAttendance
        :classMeeting="attendanceDialog.classMeeting"
        @cancel="cancelAttendance"
        @save="saveAttendance"
      />
    </v-dialog>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">{{
        $t("actions.close")
      }}</v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import ClassMeetingForm from "./ClassMeetingForm";
import ClassAttendance from "./ClassAttendance";

export default {
  name: "CourseOfferingMeetings",

  components: {
    ClassMeetingForm,
    ClassAttendance
  },

  data() {
    return {
      loading: true,
      loadingFailed: false,
      meetings: [],
      search: "",

      classMeetingDialog: {
        show: false,
        editMode: false,
        classMeeting: {}
      },

      attendanceDialog: {
        show: false,
        classMeeting: {}
      },

      snackbar: {
        show: false,
        text: ""
      }
    };
  },

  props: {
    offeringId: {
      type: [String, Number],
      required: true
    }
  },

  computed: {
    headers() {
      return [
        { text: this.$t("courses.when"), value: "displayDate", width: "33%" },
        {
          text: this.$t("courses.location"),
          value: "location.description",
          width: "33%"
        },
        {
          text: this.$t("courses.teacher"),
          value: "teacher.compositeName",
          width: "33%"
        },
        { text: this.$t("actions.header"), sortable: false }
      ];
    },
    ...mapGetters(["currentLanguageCode"])
  },

  watch: {
    $route: "loadMeetings",
    currentLanguageCode: "updateCompositeProperties"
  },

  methods: {
    loadMeetings() {
      this.loading = true;
      this.loadingFailed = false;
      this.$http
        .get(
          `/api/v1/courses/course_offerings/${this.offeringId}/class_meetings`
        )
        .then(resp => {
          this.meetings = resp.data;
          this.updateCompositeProperties();
        })
        .catch(err => {
          console.log("LOAD MEETINGS ERR", err);
          this.loadingFailed = true;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    updateCompositeProperties() {
      this.meetings.forEach(meeting => {
        // TODO if better, localized way to get a person's full name, use that instead of just appending names together
        meeting.teacher.compositeName =
          meeting.teacher.firstName + " " + meeting.teacher.lastName;
        meeting.displayDate = this.getDisplayDate(meeting.when);
        return meeting;
      });
    },

    activateClassMeetingDialog(classMeeting = {}, editMode = false) {
      this.classMeetingDialog.editMode = editMode;
      this.classMeetingDialog.classMeeting = classMeeting;
      this.classMeetingDialog.show = true;
    },

    editClassMeeting(classMeeting) {
      this.activateClassMeetingDialog({ ...classMeeting }, true);
    },

    newClassMeeting() {
      this.activateClassMeetingDialog();
    },

    cancelClassMeeting() {
      this.classMeetingDialog.show = false;
    },

    saveClassMeeting(meetings) {
      if (meetings instanceof Error) {
        this.snackbar.text = this.classMeetingDialog.editMode
          ? this.$t("courses.update-meeting-failed")
          : this.$t("courses.add-meeting-failed");
        this.snackbar.show = true;
        this.classMeetingDialog.show = false;
        return;
      }

      if (this.classMeetingDialog.editMode) {
        // Locate the record we're updating in the table.
        let meeting = meetings[0]; // Editing just updates a single meeting
        const idx = this.meetings.findIndex(c => c.id === meeting.id);
        Object.assign(this.meetings[idx], meeting);
        this.snackbar.text = this.$t("courses.meeting-updated");
      } else {
        for (let meeting of meetings) {
          meeting.displayDate = this.getDisplayDate(meeting.when);
          meeting.teacher.compositeName =
            meeting.teacher.firstName + " " + meeting.teacher.lastName;
        }
        this.meetings.push(...meetings);
        this.snackbar.text = this.$t("courses.meeting-added");
      }

      this.snackbar.show = true;
      this.classMeetingDialog.show = false;
    },

    openAttendance(meeting) {
      this.attendanceDialog.classMeeting = meeting;
      this.attendanceDialog.show = true;
    },

    cancelAttendance() {
      this.attendanceDialog.show = false;
    },

    saveAttendance(attendance) {
      if (attendance instanceof Error) {
        this.snackbar.text = this.$t("courses.class-attendance-update-failed");
      } else {
        this.snackbar.text = this.$t("courses.class-attendance-updated");
      }

      this.snackbar.show = true;
      this.attendanceDialog.show = false;
    },

    getDisplayDate(ts) {
      let date = new Date(ts);
      return date.toLocaleTimeString(this.currentLanguageCode, {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    }
  },

  mounted() {
    this.loadMeetings();
  }
};
</script>

<style></style>
