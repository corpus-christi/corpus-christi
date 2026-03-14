<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ t("courses.register-for-course") }}</span>
    </v-card-title>
    <v-card-text>
      <v-form>
        <v-spacer></v-spacer>
        <v-radio-group v-model="selectedOffering" name="offering">
          <span>{{ t("courses.choose-offering") }}</span>
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
        >{{ t("actions.cancel") }}</v-btn
      >
      <v-btn
        color="primary"
        v-on:click="registerPerson"
        data-cy="register"
        :loading="loading"
        >{{ t("courses.register") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { useAuthStore } from "@/stores/auth";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const authStore = useAuthStore();

const props = defineProps<{
  activeOfferings: any;
}>();

const emit = defineEmits(["cancel", "snackbar", "registered"]);

const loading = ref(false);
const selectedOffering = ref<any>(null);
const newStudent = ref<any>({});
const showExpansion = ref([false]);

function cancel() {
  clear();
  emit("cancel");
}

function clear() {
  selectedOffering.value = null;
}

function cancelNewPerson() {
  showExpansion.value = [false];
}

function savedNewPerson(person: any) {
  newStudent.value = person;
  showExpansion.value = [false];
}

function registerPerson() {
  if (!selectedOffering.value) return;
  loading.value = true;
  let my_username = authStore.currentAccount.username;
  http
    .get(`/api/v1/people/accounts/username/${my_username}`)
    .then(resp => {
      let id = resp.data.personId;
      let student: any = {};
      student.confirmed = false;
      student.offeringId = selectedOffering.value;
      student.studentId = id;
      student.active = true;
      return student;
    })
    .then(student => {
      return http.post(
        `/api/v1/courses/course_offerings/${student.studentId}`,
        student
      );
    })
    .then(resp => {
      loading.value = false;
      console.log("ADDED", resp);
      emit("snackbar", t("courses.register-success"));
      cancel();
    })
    .catch(err => {
      loading.value = false;
      console.log(err);
    });
}
</script>

<style></style>
