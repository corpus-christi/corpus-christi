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
            <v-card-title class="d-block">
              <h5 class="headline">{{ $t("diplomas.diploma") }}: {{ diploma.name }}</h5>
            </v-card-title>
            <v-subheader> {{ diploma.description }} </v-subheader>
        </template>
      </v-card>
    </v-flex>

    <!-- The tabs responsible for listing the Courses and Students -->
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
              &nbsp;{{ $t("courses.students") }}
            </v-tab>
          </v-tabs>
          <!-- The Tabs Themselves -->
          <v-tabs-items v-model="tab">
            <v-tab-item>
              <v-flex md12 v-if="!loading">
                <DiplomaCoursesTable v-bind:diploma="diploma" />
                <!-- No idea what these do. They were copied over from ui/src/components/courses/CoursesTable.vue.
                <template slot="items" slot-scope="props"> :course="course"
                  <td class="hover-hand" @click="clickThrough(props.item)">
                    {{ props.item.name }}
                  </td>
                  <td class="hover-hand" @click="clickThrough(props.item)">
                    {{ props.item.description }}
                  </td>
                </template>
                -->
              </v-flex>
            </v-tab-item>
            <v-tab-item>
              <v-flex md12 v-if="!loading">
                <DiplomaPeopleTable v-bind:diploma="diploma" />
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
import DiplomaPeopleTable from "./DiplomaPeopleTable";

export default {
  name: "DiplomaDetails",
  components: {
    DiplomaCoursesTable,
    DiplomaPeopleTable,
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

    loadCourses() {
      this.loading = true;
      this.loadingFailed = false;
      this.$http
        .get(`/api/v1/courses/diplomas/${this.diplomaID}`)
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
