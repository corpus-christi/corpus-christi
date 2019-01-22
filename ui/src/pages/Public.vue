<template>
  <v-container>
    <v-layout row>
      <v-flex xs12 sm6 md5>
        <v-toolbar color="cyan" dark style="z-index: 1">
          <v-toolbar-title>
            {{ $t("public.headers.upcoming-classes") }}
          </v-toolbar-title>
        </v-toolbar>
        <v-list style="padding-top: 0px; z-index: 0">
          <v-expansion-panel>
            <!-- TODO: filter events that have course offerings -->
            <!-- TODO: add register button function -->
            <v-expansion-panel-content
              v-for="(course, idx) in offeredCourses"
              v-bind:key="idx"
              ><div slot="header">{{ course.name }}</div>
              <v-card>
                <span class="grey--text">
                  <v-card-text>{{ course.description }}</v-card-text>
                </span>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn raised color="primary" v-on:click="registrationFormDialog.show = true">
                    {{ $t("courses.register") }}
                  </v-btn>
                  <v-spacer></v-spacer>
                </v-card-actions>
              </v-card>
              
              <v-dialog v-model="registrationFormDialog.show" max-width="500px">
                <CourseRegistrationForm 
                  v-on:cancel="cancel"
                  v-on:snackbar="showSnackbar($event)"
                  :course="course"
                  v-on:registered="registeredPerson"/>
              </v-dialog>
              <v-snackbar v-model="snackbar.show">
                {{ snackbar.text }}
                <v-btn flat @click="snackbar.show = false">
                  {{ $t("actions.close") }}
                </v-btn>
              </v-snackbar>
            </v-expansion-panel-content>
          </v-expansion-panel>
          <v-card>
            <v-card-actions>
              <v-btn
                v-on:click="$router.push({ path: '/public/courses' })"
                flat
                block
                outline
                color="primary"
                >{{ $t("public.courses.view-all") }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-list>
      </v-flex>

      <v-flex xs12 sm6 md5 offset-md2>
        <v-toolbar color="blue" dark style="z-index: 1">
          <v-toolbar-title>
            {{ $t("public.headers.upcoming-events") }}
          </v-toolbar-title>
        </v-toolbar>
        <v-list style="padding-top: 0px; z-index: 0">
          <v-expansion-panel>
            <v-expansion-panel-content
              v-for="(event, idx) in events"
              v-bind:key="idx"
            >
              <div slot="header">
                {{ event.title }} <br />
                <span class="grey--text">
                  <div>{{ getDisplayDate(event.start) }}</div>
                </span>
              </div>
              <v-card>
                <v-card-text>{{ event.description }}</v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn raised color="primary">{{
                    $t("public.events.join")
                  }}</v-btn>
                  <v-spacer></v-spacer>
                </v-card-actions>
              </v-card>
            </v-expansion-panel-content>
          </v-expansion-panel>
          <!-- <v-divider light></v-divider> -->
          <v-card>
            <v-card-actions>
              <v-btn
                v-on:click="$router.push({ path: '/public/events' })"
                flat
                block
                outline
                color="primary"
                >{{ $t("public.events.view-all") }}</v-btn
              >
            </v-card-actions>
          </v-card>
        </v-list>
      </v-flex>
    </v-layout>

    <v-layout class="mt-3">
      <v-flex>
        <v-toolbar color="blue" dark>
          <v-toolbar-title data-cy="church-sentence">
            {{ $t("public.headers.home-church") }}
          </v-toolbar-title>
        </v-toolbar>
        <GoogleMap v-bind:markers="groupLocations"></GoogleMap>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import GoogleMap from "../components/GoogleMap";
import { isEmpty } from "lodash";
import CourseRegistrationForm from "../components/public/CourseRegistrationForm";

export default {
  name: "Public",
  components: { GoogleMap, CourseRegistrationForm },
  data() {
    return {
      events: [],
      courses: [],
      pageLoaded: false,
      groupLocations: [],
      
      registrationFormDialog: {
        show: false,
        editMode: false,
        saving: false,
        courseOffering: {}
      },
      
      snackbar: {
        show: false,
        message: ""
      }
    };
  },
  
  computed: {
    offeredCourses: function() {
      return this.courses.filter(course => {
        return !isEmpty(course.course_offerings);
      });
    }
  },

  mounted() {
    this.pageLoaded = false;
    this.$http.get(`/api/v1/events/?return_group=all`).then(resp => {
      this.events = resp.data;
      this.events = this.events.slice(0, 5);
      console.log(resp.data);
    });

    this.$http.get("/api/v1/courses/courses").then(resp => {
      this.courses = resp.data;
      this.courses = this.courses.slice(0, 5);
      console.log(resp.data);
      this.pageLoaded = true;
    });
  },

  methods: {
    getDisplayDate(ts) {
      let date = new Date(ts);
      return date.toLocaleTimeString(this.currentLanguageCode, {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    },

    getHomegroupLocations() {
      this.$httpNoAuth
        .get("/api/v1/places/locations")
        .then(resp => {
          console.log(resp);
          for (let loc of resp.data) {
            this.groupLocations.push({
              position: {
                lat: loc.address.latitude,
                lng: loc.address.longitude
              }
            });
          }
        })
        .catch(err => console.log("FAILED", err));
    },
    
    cancel() {
      this.registrationFormDialog.show = false;
    },
    
    registeredPerson() {
      this.registrationFormDialog.show = false;
    },
    
    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    }
  }
};
</script>
