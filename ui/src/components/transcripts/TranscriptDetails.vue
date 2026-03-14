<template>
  <v-row wrap>
    <v-col cols="12">
      <v-btn
        variant="outlined"
        color="primary"
        v-on:click="router.push({ name: 'all-transcripts' })"
        ><v-icon>arrow_back</v-icon>{{ t("actions.back") }}</v-btn
      >
    </v-col>
    <v-col cols="12" sm="8" offset-sm="2">
      <v-card>
        <template v-if="loading">
          <v-container>
            <v-row align="center" justify="center">
              <v-progress-circular color="primary" indeterminate />
            </v-row>
          </v-container>
        </template>
        <template v-else>
          <v-row>
            <v-col cols="12">
              <v-card>
                <v-toolbar color="primary">
                  <v-toolbar-title>
                    {{ t("transcripts.page-title") }}
                    {{ transcript.person.firstName }}
                    {{ transcript.person.lastName }}
                    <span v-if="transcript.person.secondLastName">{{
                      transcript.person.secondLastName
                    }}</span>
                  </v-toolbar-title>
                </v-toolbar>

                <v-list-subheader>
                  <h2>{{ t("transcripts.student-information") }}:</h2>
                </v-list-subheader>
                <v-row>
                  <v-col cols="12" sm="10" offset-sm="1">
                    <div>
                      <span class="font-weight-bold"
                        >{{ t("person.name.first") }}:
                      </span>
                      {{ transcript.person.firstName }}
                    </div>
                    <div>
                      <span class="font-weight-bold"
                        >{{ t("person.name.last") }}: </span
                      >{{ transcript.person.lastName }}
                    </div>
                    <div v-if="transcript.person.secondLastName">
                      <span class="font-weight-bold"
                        >{{ t("person.name.second-last") }}: </span
                      >{{ transcript.person.secondLastName }}
                    </div>
                    <div>
                      <span class="font-weight-bold"
                        >{{ t("person.email") }}: </span
                      >{{ transcript.person.email }}
                    </div>
                    <div>
                      <span class="font-weight-bold"
                        >{{ t("person.phone") }}: </span
                      >{{ transcript.person.phone }}
                    </div>
                    <div>
                      <span class="font-weight-bold"
                        >{{ t("person.date.birthday") }}: </span
                      >{{ transcript.person.birthday }}
                    </div>
                  </v-col>
                </v-row>
                <v-list-subheader>
                  <h2>{{ t("diplomas.diplomas") }}:</h2>
                  <v-spacer></v-spacer>
                  <v-btn
                    color="primary"
                    variant="elevated"
                    v-on:click.stop="newDiploma"
                    data-cy="add-diploma-this-student"
                  >
                    <v-icon left>library_add</v-icon>
                    {{ t("transcripts.add-diploma-this-student") }}
                  </v-btn>
                </v-list-subheader>
                <v-row>
                  <v-col cols="12" sm="10" offset-sm="1">
                    <div
                      v-for="diploma in transcript.diplomaList"
                      :key="`diploma-` + `${diploma.id}`"
                    >
                      <!-- making a composite key to avoid duplicate key issue: https://github.com/vuejs/vue/issues/7323 -->
                      <h3>{{ diploma.name }}:</h3>
                      <ul class="mb-2">
                        <li
                          v-for="(diplomaCourse, diplomaCourseIndex) in diploma.courses"
                          :key="`diplomaCourse-` + `${diplomaCourseIndex}`"
                        >
                          {{ diplomaCourse.name }}
                          <span
                            v-if="diplomaCourse.courseCompleted"
                            class="text-green"
                            >{{ t("transcripts.course-completed") }}</span
                          >
                        </li>
                      </ul>
                    </div>
                  </v-col>
                </v-row>
                <v-list-subheader>
                  <h2>
                    {{ t("transcripts.courses-in-progress-or-completed") }}:
                  </h2>
                </v-list-subheader>
                <v-row>
                  <v-col cols="12" sm="10" offset-sm="1">
                    <div
                      v-for="(course, courseIndex) in transcript.courses"
                      :key="`course-` + `${courseIndex}`"
                    >
                      <!-- making a composite key to avoid duplicate key issue: https://github.com/vuejs/vue/issues/7323 -->
                      <h3>
                        {{ course.name }}:
                        <span
                          v-if="course.courseCompleted"
                          class="text-green"
                          >{{ t("transcripts.course-completed") }}</span
                        >
                      </h3>
                      <ul class="mb-2">
                        <li
                          v-for="(courseOffering, index) in course.courseOfferings"
                          :key="`courseOffering-` + `${index}`"
                        >
                          {{ courseOffering.description }}
                        </li>
                      </ul>
                    </div>
                  </v-col>
                </v-row>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </v-card>
    </v-col>
    <!-- New/Edit dialog -->
    <v-dialog v-model="diplomaDialog.show" max-width="500px" persistent>
      <AddDiplomaEditor
        v-bind:saving="diplomaDialog.saving"
        v-bind:diplomasThisStudent="diplomasThisStudent"
        v-on:cancel="cancelDiploma"
        v-on:save="saveDiploma"
      />
    </v-dialog>
  </v-row>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter, useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import AddDiplomaEditor from "./AddDiplomaEditor.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const router = useRouter();
const route = useRoute();

const props = defineProps<{
  studentId: string | number;
}>();

const diplomaDialog = ref({
  show: false,
  saving: false
});

const diplomasThisStudent = ref<any[]>([]);
const transcript = ref<any>({});
const loading = ref(true);
const loadingFailed = ref(false);

function loadTranscript() {
  loading.value = true;
  loadingFailed.value = false;
  http
    .get(`/api/v1/courses/students/${props.studentId}`)
    .then(resp => {
      transcript.value = resp.data;
      console.log("transcript for this student: ", transcript.value);
    })
    .catch(() => {
      loadingFailed.value = true;
    })
    .finally(() => {
      loading.value = false;
    });
}

function activateDiplomaDialog() {
  diplomasThisStudent.value = [];
  transcript.value.diplomaList.forEach((diploma: any) => {
    diplomasThisStudent.value.push(diploma.id);
  });
  diplomaDialog.value.show = true;
}

function newDiploma() {
  activateDiplomaDialog();
}

function cancelDiploma() {
  diplomaDialog.value.show = false;
}

function saveDiploma(diploma: any) {
  console.log("save diploma");
  let diplomaAwarded = {
    personId: transcript.value.person.id,
    diplomaId: diploma.id,
    when: null
  };
  http
    .post("/api/v1/courses/diplomas_awarded", diplomaAwarded)
    .then(resp => {
      console.log("ADDED", resp);
      loadTranscript();
    })
    .catch(err => {
      console.error("FAILURE", err);
    })
    .finally(() => {
      diplomaDialog.value.show = false;
      diplomaDialog.value.saving = false;
    });
}

watch(route, () => {
  loadTranscript();
});

onMounted(() => {
  loadTranscript();
});
</script>

<style></style>
