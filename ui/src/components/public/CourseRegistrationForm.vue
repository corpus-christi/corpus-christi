<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ $t("courses.register-for-course") }}</span>
    </v-card-title>
    <v-card-text>
      <v-form>
        <v-spacer></v-spacer>
        <v-radio-group
          v-model="selectedOffering"
          v-validate="'required'"
          name="offering"
          v-bind:error-messages="errors.first('offering')"
        >
          <span>{{ $t("courses.choose-offering") }}</span>
          <v-radio
            v-for="offering in activeOfferings"
            :key="offering.id"
            :value="offering.id"
            :label="`${offering.description}`"
            type="radio"
            data-cy="offering-selection"
          ></v-radio>
        </v-radio-group>
      </v-form>
    </v-card-text>

    <!-- cancel and register buttons -->
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        v-on:click="cancel"
        data-cy="cancel"
        :disabled="loading"
        >{{ $t("actions.cancel") }}</v-btn
      >
      <v-btn
        color="primary"
        v-on:click="registerPerson"
        data-cy="register"
        :loading="loading"
        >{{ $t("courses.register") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  name: "CourseRegistrationForm",
  data() {
    return {
      username: "",
      password: "",
      loading: false,
      selectedOffering: null,
      newStudent: {},
      showExpansion: [false]
    };
  },

  props: {
    activeOfferings: null
  },

  computed: mapGetters(["isLoggedIn", "currentAccount"]),

  methods: {
    cancel() {
      this.clear();
      this.$validator.reset();
      this.$emit("cancel");
    },
    register() {
      // TODO: course-offering-students
    },
    clear() {
      this.selectedOffering = null;
    },
    cancelNewPerson() {
      this.showExpansion = [false];
    },

    savedNewPerson(person) {
      this.newStudent = person;
      this.showExpansion = [false];
    },

    registerPerson() {
      //temporary for presentation! fix me later!!
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.loading = true;
          let my_username = this.currentAccount.username;
          this.$http
            .get(`/api/v1/people/accounts/username/${my_username}`)
            .then(resp => {
              let id = resp.data.personId;
              let newStudent = {};
              newStudent.confirmed = false;
              newStudent.offeringId = this.selectedOffering;
              newStudent.studentId = id;
              newStudent.active = true;
              return newStudent;
            })
            .then(student => {
              return this.$http.post(
                `/api/v1/courses/course_offerings/${student.studentId}`,
                student
              );
            })
            .then(resp => {
              this.loading = false;
              console.log("ADDED", resp);
              this.$emit("snackbar", this.$t("courses.register-success"));
              this.cancel();
            })
            .catch(err => {
              this.loading = false;
              console.log(err);
            });
        }
      });
    }
  }
};
</script>

<style></style>
