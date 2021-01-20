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
    <v-flex xs12 sm8 offset-sm2>
      <template v-if="loading">
        <v-container fill-height fluid>
          <v-layout xs12 align-center justify-center>
            <v-progress-circular color="primary" indeterminate />
          </v-layout>
        </v-container>
      </template>
      <template v-else>
        <v-card>
          <v-tabs v-model="tab" color="primary" slider-color="accent">
            <v-tab ripple data-cy="roles-table-tab">
              <v-icon>person</v-icon>
              &nbsp;{{ $t("people.title") }}
            </v-tab>
          </v-tabs>
          <v-tabs-items v-model="tab">
            <v-tab-item>
              <v-layout row>
                <v-flex xs12>
                  <v-card>
                    <v-toolbar primary>
                      <v-toolbar-title>
                        {{ $t("diplomas.diploma") }}: {{ diploma.name }}
                      </v-toolbar-title>
                    </v-toolbar>
                    <v-list three-line>
                      <v-subheader> {{ diploma.description }} </v-subheader>
                      <v-subheader
                        >{{ $t("diplomas.courses-this-diploma") }}:</v-subheader
                      >
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
                  </v-card>
                </v-flex>
              </v-layout>
            </v-tab-item>
          </v-tabs-items>
        </v-card>
      </template>
    </v-flex>
  </v-layout>
</template>

<script>
export default {
  name: "DiplomaDetails",
  components: {},
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
