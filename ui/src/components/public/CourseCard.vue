<template>
  <div>
    <v-card class="card elevation-10">
      <div class="body">
        <!-- Display course title, description and register button -->
        <v-card-title style="text-align: center" class="title">
          <v-row align="center" justify="center">
            <v-col shrink>
              <span class="headline mb-3">{{ course.name }}</span>
            </v-col>
          </v-row>
        </v-card-title>
        <v-row>
          <v-card-text class="text" style="text-align: center">
            <v-col>
              <b>{{ t("courses.description") }}: </b>
              <div class="mb-3">{{ course.description }}</div>
            </v-col>
          </v-card-text>
        </v-row>
        <v-row>
          <v-col>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                rounded
                variant="elevated"
                color="primary"
                @click="registerClicked(course)"
              >
                {{ t("courses.register") }}
              </v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-col>
        </v-row>
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
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">
          {{ t("actions.close") }}
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import CourseRegistrationForm from "./CourseRegistrationForm.vue";

const { t } = useI18n();

const props = defineProps<{
  course: any;
}>();

const registrationFormDialog = ref({
  show: false,
  editMode: false,
  saving: false,
  courseOffering: {} as any
});

const snackbar = ref({
  show: false,
  text: ""
});

const activeOfferings = ref<any>(null);

function cancel() {
  registrationFormDialog.value.show = false;
}

function registeredPerson() {
  registrationFormDialog.value.show = false;
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

function registerClicked(course: any) {
  activeOfferings.value = course.course_offerings.filter(
    (courseOffering: any) => courseOffering.active
  );
  registrationFormDialog.value.show = true;
}
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
