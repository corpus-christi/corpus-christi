<template>
  <v-layout row wrap>
    <v-flex xs12>
      <v-btn
        outline
        color="primary"
        v-on:click="$router.push({ name: 'all-transcripts' })"
      ><v-icon>arrow_back</v-icon>{{ $t("actions.back") }}</v-btn>
    </v-flex>
    <v-flex xs12 sm8 offset-sm2>
      <v-card>
        <v-img
          src="https://cdn.vuetifyjs.com/images/cards/desert.jpg"
          aspect-ratio="2.75"
        ></v-img>
        <template v-if="loading">
          <v-container fill-height fluid>
            <v-layout xs12 align-center justify-center>
              <v-progress-circular color="primary" indeterminate/>
            </v-layout>
          </v-container>
        </template>
        <template v-else>
            <v-container>
                <v-layout xs12 align-center justify-center>
                    <v-card-title primary-title>
                        <h3 class="headline mb-0">
                            {{ $t("transcripts.page-title")}} {{ transcript.person.firstName }} {{ transcript.person.lastName }}
                        </h3>
                    </v-card-title>
                </v-layout>
            </v-container>
            

            <v-card-text>
                <h4>
                    {{ $t("transcripts.student-information") }}
                </h4>
               
                <div> 
                    {{ $t("person.name.first") }}:  {{ transcript.person.firstName }} 
                </div>
                <div>
                    {{ $t("person.name.last") }}:  {{ transcript.person.lastName }} 
                </div>
                <div> 
                    {{ $t("person.email") }}:  {{ transcript.person.email }} 
                </div>
                <div> 
                    {{ $t("person.phone") }}:  {{ transcript.person.phone }} 
                </div>
                <div> 
                    {{ $t("person.date.birthday") }}:  {{ transcript.person.birthday }} 
                </div>
                

<!--
     "active": true,
          
          
          "gender": "M",
          "id": 1,
          
          "locationId": null,
          "phone": "410-122-9419x6396"
          -->

                <v-divider></v-divider>

            </v-card-text>    
            <v-card-actions>
            <v-btn flat color="orange">Share</v-btn>
            <v-btn flat color="orange">Explore</v-btn>
            </v-card-actions>
        </template>
      </v-card>
    </v-flex>
  </v-layout>
</template>

<!--
<template>
  <v-layout row wrap>
    <v-flex xs12>
      <v-btn
        outline
        color="primary"
        v-on:click="$router.push({ name: 'all-transcripts' })"
      ><v-icon>arrow_back</v-icon>{{ $t("actions.back") }}</v-btn>
    </v-flex>
    <v-flex sm12 md3>
      <v-card>
        <template v-if="loading">
          <v-container fill-height fluid>
            <v-layout xs12 align-center justify-center>
              <v-progress-circular color="primary" indeterminate/>
            </v-layout>
          </v-container>
        </template>
        <template v-else>
          <v-card-title class="d-block">
            <h5 class="headline">{{ transcript.person.firstName }} {{ transcript.person.lastName }}</h5>
            <span class="caption" v-if="!course.active">
              <v-icon small>archive</v-icon>
              {{ $t("courses.is-archived") }}
            </span>
          </v-card-title>
          <v-card-text>
            {{ course.description }}
          </v-card-text>
        </template>
      </v-card>
      <v-card class="mt-2" v-if="!loading">
        <template v-if="course.prerequisites.length > 0">
          <v-card-title>
            <h5 class="headline">{{ $t("courses.prerequisites") }}</h5>
          </v-card-title>
          <v-card-text>
            <v-list dense>
              <v-list-tile
                v-for="prereq of course.prerequisites"
                :key="prereq.id"
                :to="{ name: 'course-details', params: { courseId: prereq.id } }">
                {{ prereq.name }}
              </v-list-tile>
            </v-list>
          </v-card-text>
        </template>
        <template v-else>
          <v-card-text>
            {{ $t("courses.no-prerequisites") }}
          </v-card-text>
        </template>
      </v-card>
    </v-flex>
    <v-flex sm12 md9 class="pl-2" v-if="!loading">
      <CourseOfferingsTable :course="course"/>
    </v-flex>
  </v-layout>
</template>
-->

<script>
export default {
  name: "TranscriptDetails",
  components: {
  },
  props: {
    studentId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      transcript: { }, //prerequisites: [] },
      loading: true,
      loadingFailed: false
    };
  },
  mounted() { 
    this.loadCourse();
  },
  watch: {
    $route: "loadCourse"
  },
  methods: {
    loadCourse() {
      this.loading = true;
      this.loadingFailed = false;
      //this.$http.get(`/api/v1/courses/courses/${this.courseId}`)
      this.$http.get("http://localhost:3000/students")
        .then(resp => {
            //FIX THIS!
          this.transcript = resp.data[0];
        })
        .catch(() => {
          this.loadingFailed = true;
        })
        .finally(() => {
          this.loading = false;
        });
    }
  }
}
</script>

<style>

</style>
