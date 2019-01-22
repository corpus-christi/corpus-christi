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
                <template v-if="loading">
                    <v-container fill-height fluid>
                        <v-layout xs12 align-center justify-center>
                        <v-progress-circular color="primary" indeterminate/>
                        </v-layout>
                    </v-container>
                </template>
                <template v-else>
                    <v-layout row>
                        <v-flex xs12>
                            <v-card>
                                <v-toolbar primary>
                                    <v-toolbar-title>
                                        {{ $t("transcripts.page-title")}} {{ transcript.person.firstName }} {{ transcript.person.lastName }}
                                        <span v-if="transcript.person.secondLastName">{{ transcript.person.secondLastName }}</span>
                                    </v-toolbar-title>
                                </v-toolbar>
                                <v-list three-line>
                                    <v-subheader >
                                        {{ $t("transcripts.student-information") }}:
                                    </v-subheader>
                                    <v-layout row>
                                        <v-flex xs12 sm10 offset-sm1>
                                        <div> 
                                            <span class="font-weight-bold">{{ $t("person.name.first") }}: </span> {{ transcript.person.firstName }} 
                                        </div>
                                        <div>
                                            <span class="font-weight-bold">{{ $t("person.name.last") }}:  </span>{{ transcript.person.lastName }} 
                                        </div>
                                        <div v-if="transcript.person.secondLastName">
                                            <span class="font-weight-bold">{{ $t("person.name.second-last") }}:  </span>{{ transcript.person.secondLastName }}
                                        </div>
                                        <div> 
                                            <span class="font-weight-bold">{{ $t("person.email") }}:  </span>{{ transcript.person.email }} 
                                        </div>
                                        <div> 
                                            <span class="font-weight-bold">{{ $t("person.phone") }}:  </span>{{ transcript.person.phone }} 
                                        </div>
                                        <div> 
                                            <span class="font-weight-bold">{{ $t("person.date.birthday") }}:  </span>{{ transcript.person.birthday }} 
                                        </div>
                                    </v-flex>
                                </v-layout>
                                <v-subheader >
                                    {{ $t("diplomas.diplomas") }}:
                                    <v-spacer></v-spacer>
                                        <v-btn
                                            color="primary"
                                            raised
                                            v-on:click.stop="newDiploma"
                                            data-cy="add-diploma-this-student"
                                        >
                                            <v-icon left>library_add</v-icon>
                                            {{ $t("diplomas.new") }}
                                        </v-btn>
                                </v-subheader>
                                <template v-for="(diploma, diplomaIndex) in transcript.diplomaList">
                                    <v-list-tile
                                        :key=diplomaIndex
                                    >
                                    <v-list-tile-content>
                                        <v-list-tile-title><span class="font-weight-bold">{{diploma.name}}</span></v-list-tile-title>
                                        - ...list of courses required to complete this diploma... -
                                    </v-list-tile-content>
                                    </v-list-tile>
                                </template>

                                <v-subheader >
                                    {{ $t("transcripts.courses") }}:
                                </v-subheader>
                                <template v-for="(course, index) in transcript.courses">
                                    <!-- making a composite key to avoid duplicate key issue: https://github.com/vuejs/vue/issues/7323 -->
                                    <v-list-tile
                                        :key="course+`${index}`"
                                    >
                                    <v-list-tile-content>
                                        <v-list-tile-title><span class="font-weight-bold">{{course.name}}:</span> {{course.description}}

                                        </v-list-tile-title>
                                        <ul>
                                            <li v-for="courseOffering in course.courseOfferings" :key="courseOffering.id">
                                                {{courseOffering.description}}
                                            </li>
                                        </ul>
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
<!--
<template>
  
    <v-flex xs12 sm8 offset-sm2>
      <v-card>
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
                


     "active": true,
          
          
          "gender": "M",
          "id": 1,
          
          "locationId": null,
          "phone": "410-122-9419x6396"
        

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
      this.$http.get(`/api/v1/courses/students/${this.studentId}`)
        .then(resp => {
          this.transcript = resp.data;
          console.log('transcript for this student: ', this.transcript);
        })
        .catch(() => {
          this.loadingFailed = true;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    newDiploma() {
        console.log('add diploma');
    }
  }
}
</script>

<style>

</style>
