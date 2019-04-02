<template>
  <div>
    <v-card class="card elevation-10">
      <div class="body">
        <!-- Display course title, description and register button -->
        <v-card-title style="text-align: center" class="title">
          <v-layout row align-center justify-center>
            <v-flex shrink>
              <span class="headline mb-3">{{ course.name }}</span>
            </v-flex>
          </v-layout>
        </v-card-title>
        <v-layout>
          <v-card-text class="text" style="text-align: center">
            <v-flex>
              <b>{{ $t("courses.description") }}: </b>
              <div class="mb-3">{{ course.description }}</div>
            </v-flex>
          </v-card-text>
        </v-layout>
        <v-layout>
          <v-flex align-self-baseline>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                round
                raised
                color="primary"
                @click="registerClicked(course)"
              >
                {{ $t("courses.register") }}
              </v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-flex>
        </v-layout>
      </div>
    </v-card>
    <v-dialog v-model="registrationFormDialog.show" max-width="500px">
      <CourseRegistrationForm
        v-on:cancel="cancel"
        v-on:snackbar="showSnackbar($event)"
        :activeOfferings="activeOfferings"
        v-on:registered="registeredPerson"
      />
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
import CourseRegistrationForm from "./CourseRegistrationForm";

export default {
  name: "CourseCard",
  props: {
    course: {}
  },
  components: {
    CourseRegistrationForm
  },
  data() {
    return {
      registrationFormDialog: {
        show: false,
        editMode: false,
        saving: false,
        courseOffering: {}
      },
      snackbar: {
        show: false,
        message: ""
      },

      activeOfferings: null
    };
  },

  methods: {
    cancel() {
      this.registrationFormDialog.show = false;
    },
    registeredPerson() {
      this.registrationFormDialog.show = false;
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    registerClicked(course) {
      this.activeOfferings = course.course_offerings.filter(
        courseOffering => courseOffering.active
      );

      this.registrationFormDialog.show = true;
    }
  }
};
</script>

<style scoped>
.text {
  max-height: 125px;
  min-height: 125px;
}

.title {
  max-height: 105px;
  min-height: 105px;
}

.card {
  margin: 25px;
  border-radius: 30px;
  max-height: 350px;
  min-height: 350px;
}

.body {
  padding-top: 10px;
  border-radius: 30px;
}
</style>
