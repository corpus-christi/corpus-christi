<template>
  <v-layout row wrap>
    <v-flex xs12>
      <v-btn
        outline
        color="primary"
        v-on:click="$router.push({ name: 'all-transcripts' })"
        ><v-icon>arrow_back</v-icon>{{ $t("actions.back") }}</v-btn
      >
    </v-flex>
    <v-flex xs12 sm8 offset-sm2>
      <v-card>
        <template v-if="loading">
          <v-container fill-height fluid>
            <v-layout xs12 align-center justify-center>
              <v-progress-circular color="primary" indeterminate />
            </v-layout>
          </v-container>
        </template>
        <template v-else>
          <v-layout row>
            <v-flex xs12>
              <v-card>
                <v-toolbar primary>
                  <v-toolbar-title>
                    {{ $t("transcripts.page-title") }}
                    {{ transcript.person.firstName }}
                    {{ transcript.person.lastName }}
                    <span v-if="transcript.person.secondLastName">{{
                      transcript.person.secondLastName
                    }}</span>
                  </v-toolbar-title>
                </v-toolbar>

                <v-subheader>
                  <h2>{{ $t("transcripts.student-information") }}:</h2>
                </v-subheader>
                <v-layout row>
                  <v-flex xs12 sm10 offset-sm1>
                    <div>
                      <span class="font-weight-bold"
                        >{{ $t("person.name.first") }}:
                      </span>
                      {{ transcript.person.firstName }}
                    </div>
                    <div>
                      <span class="font-weight-bold"
                        >{{ $t("person.name.last") }}: </span
                      >{{ transcript.person.lastName }}
                    </div>
                    <div v-if="transcript.person.secondLastName">
                      <span class="font-weight-bold"
                        >{{ $t("person.name.second-last") }}: </span
                      >{{ transcript.person.secondLastName }}
                    </div>
                    <div>
                      <span class="font-weight-bold"
                        >{{ $t("person.email") }}: </span
                      >{{ transcript.person.email }}
                    </div>
                    <div>
                      <span class="font-weight-bold"
                        >{{ $t("person.phone") }}: </span
                      >{{ transcript.person.phone }}
                    </div>
                    <div>
                      <span class="font-weight-bold"
                        >{{ $t("person.date.birthday") }}: </span
                      >{{ transcript.person.birthday }}
                    </div>
                  </v-flex>
                </v-layout>
                <v-subheader>
                  <h2>{{ $t("diplomas.diplomas") }}:</h2>
                  <v-spacer></v-spacer>
                  <v-btn
                    color="primary"
                    raised
                    v-on:click.stop="newDiploma"
                    data-cy="add-diploma-this-student"
                  >
                    <v-icon left>library_add</v-icon>
                    {{ $t("transcripts.add-diploma-this-student") }}
                  </v-btn>
                </v-subheader>
                <v-layout row>
                  <v-flex xs12 sm10 offset-sm1>
                    <div
                      v-for="diploma in transcript.diplomaList"
                      :key="`diploma-` + `${diploma.id}`"
                    >
                      <!-- making a composite key to avoid duplicate key issue: https://github.com/vuejs/vue/issues/7323 -->
                      <h3>{{ diploma.name }}:</h3>
                      <ul class="mb-2">
                        <li
                          v-for="(diplomaCourse,
                          diplomaCourseIndex) in diploma.courses"
                          :key="`diplomaCourse-` + `${diplomaCourseIndex}`"
                        >
                          {{ diplomaCourse.name }}
                          <span
                            v-if="diplomaCourse.courseCompleted"
                            class="green--text"
                            >{{ $t("transcripts.course-completed") }}</span
                          >
                        </li>
                      </ul>
                    </div>
                  </v-flex>
                </v-layout>
                <v-subheader>
                  <h2>
                    {{ $t("transcripts.courses-in-progress-or-completed") }}:
                  </h2>
                </v-subheader>
                <v-layout row>
                  <v-flex xs12 sm10 offset-sm1>
                    <div
                      v-for="(course, courseIndex) in transcript.courses"
                      :key="`course-` + `${courseIndex}`"
                    >
                      <!-- making a composite key to avoid duplicate key issue: https://github.com/vuejs/vue/issues/7323 -->
                      <h3>
                        {{ course.name }}:
                        <span
                          v-if="course.courseCompleted"
                          class="green--text"
                          >{{ $t("transcripts.course-completed") }}</span
                        >
                      </h3>
                      <ul class="mb-2">
                        <li
                          v-for="(courseOffering,
                          index) in course.courseOfferings"
                          :key="`courseOffering-` + `${index}`"
                        >
                          {{ courseOffering.description }}
                        </li>
                      </ul>
                    </div>
                  </v-flex>
                </v-layout>
              </v-card>
            </v-flex>
          </v-layout>
        </template>
      </v-card>
    </v-flex>
    <!-- New/Edit dialog -->
    <v-dialog v-model="diplomaDialog.show" max-width="500px" persistent>
      <AddDiplomaEditor
        v-bind:saving="diplomaDialog.saving"
        v-bind:diplomasThisStudent="diplomasThisStudent"
        v-on:cancel="cancelDiploma"
        v-on:save="saveDiploma"
      />
    </v-dialog>
  </v-layout>
</template>

<script>
import AddDiplomaEditor from "./AddDiplomaEditor";
export default {
  name: "TranscriptDetails",
  components: {
    AddDiplomaEditor
  },
  props: {
    studentId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      diplomaDialog: {
        show: false,
        saving: false
      },
      diplomasThisStudent: [],
      transcript: {},
      personalInformation: [],
      loading: true,
      loadingFailed: false
    };
  },
  mounted() {
    this.loadTranscript();
  },
  watch: {
    $route: "loadTranscript"
  },
  methods: {
    loadTranscript() {
      this.loading = true;
      this.loadingFailed = false;
      this.$http
        .get(`/api/v1/courses/students/${this.studentId}`)
        .then(resp => {
          this.transcript = resp.data;
          console.log("transcript for this student: ", this.transcript);
        })
        .catch(() => {
          this.loadingFailed = true;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    activateDiplomaDialog() {
      this.transcript.diplomaList.forEach(diploma => {
        this.diplomasThisStudent.push(diploma.id);
      });
      this.diplomaDialog.show = true;
    },
    newDiploma() {
      this.activateDiplomaDialog();
    },
    cancelDiploma() {
      this.diplomaDialog.show = false;
    },
    saveDiploma(diploma) {
      console.log("save diploma");
      let diplomaAwarded = {
        personId: this.transcript.person.id,
        diplomaId: diploma.id,
        when: null
      };
      this.$http
        .post("/api/v1/courses/diplomas_awarded", diplomaAwarded)
        .then(resp => {
          console.log("ADDED", resp);
          // Not used?? let newDiploma = resp.data;
          this.loadTranscript();
        })
        .catch(err => {
          console.error("FAILURE", err);
          this.snackbar.text = this.$t("diplomas.add-failed");
          this.snackbar.show = true;
        })
        .finally(() => {
          this.diplomaDialog.show = false;
          this.diplomaDialog.saving = false;
        });
    }
  }
};
</script>

<style></style>
