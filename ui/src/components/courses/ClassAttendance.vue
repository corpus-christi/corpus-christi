<template>
  <v-card>
    <v-card-title>
      <span class="headline">
        {{ $t("courses.class-attendance-for") }}
        {{ getDisplayDate(classMeeting.when) }}
      </span>
    </v-card-title>
    <v-card-text>
      <template v-if="loading">
        <v-progress-linear indeterminate color="primary" />
      </template>
      <template v-else-if="loadingFailed">
        {{ $t("courses.class-attendance-load-failed") }}
      </template>
      <template v-else>
        <v-list>
          <v-list-tile v-for="student of students" :key="student.id">
            <v-list-tile-action>
              <v-checkbox v-model="student.present" />
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>
                {{ student.person.firstName }} {{ student.person.lastName }}
              </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list>
      </template>
    </v-card-text>
    <v-card-actions>
      <v-btn color="secondary" flat :disabled="saving" v-on:click="cancel">{{
        $t("actions.cancel")
      }}</v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        raised
        :disabled="saving"
        :loading="saving"
        v-on:click="save"
      >
        {{ $t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: "ClassAttendance",
  props: {
    classMeeting: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      loadingFailed: false,
      saving: false,

      students: []
    };
  },
  watch: {
    classMeeting: "load"
  },
  methods: {
    load() {
      this.loading = true;
      this.loadingFailed = false;

      let promises = [];
      promises.push(
        this.$http
          .get(
            `/api/v1/courses/course_offerings/${this.classMeeting.offeringId}/${
              this.classMeeting.id
            }/class_attendance`
          )
          .then(resp => resp.data.attendance)
      );

      promises.push(
        this.$http
          .get(
            `/api/v1/courses/course_offerings/${
              this.classMeeting.offeringId
            }/students`
          )
          .then(resp => {
            this.students = resp.data.filter(
              student => student.active && student.confirmed
            );
          })
      );

      Promise.all(promises)
        .then(values => {
          let attendance = values[0];
          this.applyAttendance(attendance);
        })
        .catch(err => {
          console.log("LOAD ERR", err);
          this.loadingFailed = true;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    applyAttendance(attendance) {
      this.students.forEach(student => {
        student.present = !!attendance.find(
          record => record.studentId == student.id
        );
      });
    },

    clear() {
      // TODO: write a clear function that unchecks the checkboxes (NO UI BUTTON FOR THIS; ONLY CALLED FROM 'cancel()')
    },

    cancel() {
      this.clear();
      this.$emit("cancel");
    },

    save() {
      this.saving = true;
      let attendance = this.students
        .filter(student => student.present)
        .map(student => student.id);

      this.$http
        .patch(
          `/api/v1/courses/course_offerings/${this.classMeeting.offeringId}/${
            this.classMeeting.id
          }/class_attendance`,
          { attendance }
        )
        .then(resp => {
          console.log("ATTENDANCE", resp);
          this.$emit("save", resp.data);
        })
        .catch(err => {
          console.log("ATTENDANCE ERR", err);
          this.$emit("save", err);
        })
        .finally(() => {
          this.saving = false;
        });
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
  }
};
</script>

<style></style>
