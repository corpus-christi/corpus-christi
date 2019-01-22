<template>
  <div>
    <v-card class="card elevation-10">
      <!-- Display course title, description and register button -->
      <v-card-title>
        <v-layout row align-center justify-center>
          <v-flex shrink>
            <span class="headline mb-3">{{ course.name }}</span>
          </v-flex>
        </v-layout>
      </v-card-title>
      <div class="body">
        <v-layout>
          <v-card-text class="text">
            <v-flex>
              <div class="mb-3">{{ course.description }}</div>
            </v-flex>
          </v-card-text>
        </v-layout>
        <v-layout>
          <v-flex>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                raised
                color="primary"
                @click="registrationFormDialog.show = true"
              >
                {{ $t("courses.course.register") }}
              </v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-flex>
        </v-layout>
      </div>
    </v-card>
    <v-dialog v-model="registrationFormDialog.show" max-width="500px">
      <courseRegistrationForm 
        v-on:cancel="cancel" 
        :course="course" 
        v-on:registered="registeredPerson"/>
    </v-dialog>
  </div>
</template>

<script>
import courseRegistrationForm from "./courseRegistrationForm";

export default {
  name: "CourseCard",
  props: {
    course: {}
  },
  components: {
    courseRegistrationForm
  },
  data() {
    return {
      registrationFormDialog: {
        show: false,
        editMode: false,
        saving: false,
        courseOffering: {}
      }
    };
  },

  methods: {
    cancel() {
      this.registrationFormDialog.show = false;
    },
    registeredPerson() {}
  }
};
</script>

<style scoped>
.text {
  max-height: 200px;
  min-height: 200px;
}

.card {
  margin: 25px;
  border-radius: 30px;
}

.body {
  padding-top: 10px;
  border-radius: 30px;
}
</style>
