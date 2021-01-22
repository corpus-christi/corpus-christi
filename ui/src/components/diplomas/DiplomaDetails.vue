<template>
  <v-layout row wrap>
    <v-flex xs12>
      <v-btn
        outlined
        color="primary"
        v-on:click="$router.push({ name: 'all-diplomas' })"
        ><v-icon>arrow_back</v-icon>{{ $t("actions.back") }}</v-btn
      >
    </v-flex>
    <!--
    <v-flex xs12 sm8 offset-sm2>
    -->
    <!-- The Card to the left with the Name and Description of the Diploma -->
    <v-flex sm12 md3>
      <v-card>
        <template v-if="loading">
          <v-container fill-height fluid>
            <v-layout xs12 align-center justify-center>
              <v-progress-circular color="primary" indeterminate />
            </v-layout>
          </v-container>
        </template>
        <template v-else>
            <!-- <v-toolbar-title> -->
            <v-card-title class="d-block">
              <h5 class="headline">{{ $t("diplomas.diploma") }}: {{ diploma.name }}</h5>
            </v-card-title>
            <!-- </v-toolbar-title> -->
            <v-subheader> {{ diploma.description }} </v-subheader>
            <!-- Lists the "Courses for this Diploma"
            <v-subheader>{{ $t("diplomas.courses-this-diploma") }}:</v-subheader>
            -->
        </template>
      </v-card>
    </v-flex>

    <!-- The tabs responsible for listing the Courses and Students xs12 sm8 -->
    <v-flex sm12 md9 class="pl-2" v-if="!loading">
      <v-card>
        <template>
          <!-- Tab Headers -->
          <v-tabs v-model="tab" color="primary" slider-color="accent">
            <v-tab ripple data-cy="roles-table-tab">
              <v-icon>school</v-icon>
              &nbsp;{{ $t("courses.course") }}
            </v-tab>
            <v-tab ripple data-cy="roles-table-tab">
              <v-icon>people</v-icon>
              &nbsp;{{ $t("people.title") }}
            </v-tab>
          </v-tabs>
          <!-- The Tabs Themselves -->
          <v-tabs-items v-model="tab">
            <v-tab-item>
              <!-- Serially written Course List (TODO: Replace with Table) -->
              <v-layout row>
                <v-flex xs12>
                  <v-list three-line>
                    <template v-for="(course, index) in diploma.courseList">
                      <v-list-item :key="index">
                        <v-list-item-content>
                          <v-list-item-title
                            v-html="course.name"
                          ></v-list-item-title>
                          <v-list-item-subtitle
                            v-html="course.description"
                          ></v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                    </template>
                  </v-list>
                </v-flex>
              </v-layout>
            </v-tab-item>
            <v-tab-item>
              <v-flex md11 class="pl-2" v-if="!loading">
              <!--
              <v-flex sm12 md9 class="pl-2" v-if="!loading">
              -->
                <DiplomaCoursesTable :course="course" />
              </v-flex>
            </v-tab-item>
          </v-tabs-items>
        </template>
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script>
import DiplomaCoursesTable from "./DiplomaCoursesTable";

export default {
  name: "DiplomaDetails",
  components: {
    DiplomaCoursesTable,
  },
  props: {
    diplomaId: {
      type: [String, Number],
      required: true,
    },
  },
  data() {
    return {
      diploma: {},
      loading: true,
      loadingFailed: false,
      tab: null,
    };
  },
  mounted() {
    this.loadDiploma();
  },
  watch: {
    $route: "loadDiploma",
  },
  methods: {
    loadDiploma() {
      this.loading = true;
      this.loadingFailed = false;
      this.$http
        .get(`/api/v1/courses/diplomas/${this.diplomaId}`)
        .then((resp) => {
          this.diploma = resp.data;
        })
        .catch(() => {
          this.loadingFailed = true;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>

<style></style>
