<template>
  <v-card>
    <v-card-title>Register for this course</v-card-title>
    <v-card-text>
      <v-form>
        <v-text-field
          v-model="username"
          v-bind:label="$t('account.username')"
          prepend-icon="person"
          type="text"
          name="username"
          data-cy="register-username"
        ></v-text-field>
        <v-text-field
          v-model="password"
          v-bind:label="$t('account.password')"
          prepend-icon="lock"
          name="password"
          type="password"
          data-cy="register-password"
        ></v-text-field>
        <!-- TODO: add create-person-form -->
    
        <v-spacer></v-spacer>
        <v-radio-group  v-model="selectedOffering">
        <span>{{ $t("courses.register.choose-offering") }}</span>
          <v-radio
            v-for="offering in course.course_offerings"
            :key="offering.id"
            :value="offering.id"
            :label="`${offering.description}`"
            type="radio"
            data-cy="offering-selection"
          ></v-radio>
        </v-radio-group>
      </v-form>
      {{ selectedOffering }}
    </v-card-text>

    <!-- cancel and register buttons -->
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" v-on:click="cancel" data-cy="cancel">{{
        $t("actions.cancel")
      }}</v-btn>
      <v-btn color="primary" v-on:click="registerPerson" data-cy="register">{{
        $t("actions.login")
      }}</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import PersonForm from "../people/PersonForm";
import mapGetters from "vuex";

export default {
  name: "courseRegistrationForm",
  components: {
    PersonForm
  },
  data() {
    return {
      username: "",
      password: "",
      selectedOffering: null,
      newStudent: {},
      showExpansion: [false]
    };
  },
  props: {
    course: {}
  },
  computed: mapGetters(["isLoggedaIn","currentAccount"]),

  methods: {
    cancel() {
      this.clear();
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
      this.newStudent = "person";
      this.showExpansion = [false];
    },

    registerPerson() {
      
    },

    saveNewStudent(newStudent) {
      this.newStudentDialog.saving = true;
      
      const personObject = newStudent;
      newStudent = {};
            
      newStudent.confirmed = true;
      newStudent.offeringId = this.offeringId;
      newStudent.studentId = personObject.id;
      newStudent.active = true;
        
      this.$http
        .post(`/api/v1/courses/course_offerings/${newStudent.studentId}`, newStudent)
        .then(resp => {
          console.log("ADDED", resp);
          this.students.push(resp.data);
          
          this.snackbar.text = this.$t("courses.added");
          this.snackbar.show = true;
        })
        .catch(err => {
           console.error("FAILURE", err.response);
           this.snackbar.text = this.$t("courses.add-failed");
           this.snackbar.show = true;
        })
        .finally(() => {
          this.newStudentDialog.show = false;
          this.newStudentDialog.saving = false;
        });
    },
  }
};
</script>

<style></style>

