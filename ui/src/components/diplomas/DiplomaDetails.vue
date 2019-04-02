<template>
  <v-layout row wrap>
    <v-flex xs12>
      <v-btn
        outline
        color="primary"
        v-on:click="$router.push({ name: 'all-diplomas' })"
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
                    {{ $t("diplomas.diploma") }}: {{ diploma.name }}
                  </v-toolbar-title>
                </v-toolbar>
                <v-list three-line>
                  <v-subheader> {{ diploma.description }} </v-subheader>
                  <v-subheader
                    >{{ $t("diplomas.courses-this-diploma") }}:</v-subheader
                  >
                  <template v-for="(course, index) in diploma.courseList">
                    <v-list-tile :key="index">
                      <v-list-tile-content>
                        <v-list-tile-title
                          v-html="course.name"
                        ></v-list-tile-title>
                        <v-list-tile-sub-title
                          v-html="course.description"
                        ></v-list-tile-sub-title>
                      </v-list-tile-content>
                    </v-list-tile>
                  </template>
                </v-list>
              </v-card>
            </v-flex>
          </v-layout>
        </template>
      </v-card>
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
      required: true
    }
  },
  data() {
    return {
      diploma: {},
      loading: true,
      loadingFailed: false
    };
  },
  mounted() {
    this.loadDiploma();
  },
  watch: {
    $route: "loadDiploma"
  },
  methods: {
    loadDiploma() {
      this.loading = true;
      this.loadingFailed = false;
      this.$http
        .get(`/api/v1/courses/diplomas/${this.diplomaId}`)
        .then(resp => {
          this.diploma = resp.data;
        })
        .catch(() => {
          this.loadingFailed = true;
        })
        .finally(() => {
          this.loading = false;
        });
    }
  }
};
</script>

<style></style>
