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
                <span>
                  <v-card-text>{{ course.description }}</v-card-text>
                </span>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn
                    raised
                    color="primary"
                    v-on:click="registerClicked(course)"
                  >
                    {{ $t("courses.register") }}
                  </v-btn>
                  <v-spacer></v-spacer>
                </v-card-actions>
              </v-card>
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

      <v-dialog v-model="registrationFormDialog.show" max-width="500px">
        <CourseRegistrationForm
          v-on:cancel="cancel"
          v-on:snackbar="showSnackbar($event)"
          :activeOfferings="activeOfferings"
          v-on:registered="registeredPerson"
        />
      </v-dialog>
      <v-snackbar v-model="snackbar.show">
        {{ snackbar.text }}
        <v-btn flat @click="snackbar.show = false">
          {{ $t("actions.close") }}
        </v-btn>
      </v-snackbar>

      <v-flex xs12 sm6 md5 offset-md2>
        <v-toolbar color="blue" dark style="z-index: 1">
          <v-toolbar-title>
            {{ $t("public.headers.upcoming-events") }}
          </v-toolbar-title>
        </v-toolbar>
        <v-list style="padding-top: 0px; z-index: 0">
          <v-expansion-panel>
            <v-expansion-panel-content
              v-for="(event, idx) in filteredEvents"
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
                >{{ $t("public.events.view-all") }}
              </v-btn>
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
        <GoogleMap v-bind:markers="homegroups"></GoogleMap>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import GoogleMap from "../components/GoogleMap";
import { isEmpty } from "lodash";
import { mapGetters } from "vuex";
import CourseRegistrationForm from "../components/public/CourseRegistrationForm";

export default {
  name: "Public",
  components: { GoogleMap, CourseRegistrationForm },
  data() {
    return {
      events: [],
      courses: [],
      pageLoaded: false,
      activeOfferings: [],

      registrationFormDialog: {
        show: false,
        editMode: false,
        saving: false,
        courseOffering: {}
      },

      snackbar: {
        show: false,
        message: ""
      },

      filterStart: "",
      filterEnd: "",
      homegroups: [],
      groupLocations: []
    };
  },

  mounted() {
    this.$http.get("/api/v1/courses/courses").then(resp => {
      this.courses = resp.data.filter(course => course.active);
      this.courses = this.courses.slice(0, 5);
    });

    this.pageLoaded = false;
    this.getHomegroupLocations();
    this.getEventData();

    this.filterStart = this.today;
    this.filterEnd = this.addDaystoDate(this.today, 30);
  },

  computed: {
    today() {
      return this.getDateFromTimestamp(Date.now());
    },

    filteredEvents() {
      const start = this.getTimestamp(this.filterStart);
      const end = this.getTimestamp(this.addDaystoDate(this.filterEnd, 1));

      // eslint-disable-next-line
      this.events = this.events.filter(
        ev => new Date(ev.start) <= end && new Date(ev.start) >= start
      );
      return this.events.slice(0, 5);
    },

    offeredCourses: function() {
      return this.courses.filter(course => {
        return !isEmpty(course.course_offerings);
      });
    },

    ...mapGetters(["currentLanguageCode"])
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

    getEventData() {
      this.pageLoaded = false;
      this.$http.get(`/api/v1/events/?return_group=all`).then(resp => {
        this.events = resp.data;
        this.events = this.events.slice(0, 5);
        this.pageLoaded = true;
      });
    },

    cancel() {
      this.registrationFormDialog.show = false;
    },

    registeredPerson() {
      this.registrationFormDialog.show = false;
    },

    registerClicked(course) {
      this.activeOfferings = course.course_offerings.filter(
        courseOffering => courseOffering.active
      );

      this.registrationFormDialog.show = true;
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    getDateFromTimestamp(ts) {
      let date = new Date(ts);
      if (date.getTime() < 86400000) {
        //ms in a day
        return "";
      }
      let yr = date.toLocaleDateString(this.currentLanguageCode, {
        year: "numeric"
      });
      let mo = date.toLocaleDateString(this.currentLanguageCode, {
        month: "2-digit"
      });
      let da = date.toLocaleDateString(this.currentLanguageCode, {
        day: "2-digit"
      });
      return `${yr}-${mo}-${da}`;
    },

    getTimestamp(date) {
      let datems = new Date(date).getTime();
      let tzoffset = new Date().getTimezoneOffset() * 60000;
      return new Date(datems + tzoffset);
    },

    addDaystoDate(date, dayDuration) {
      let date1 = this.getTimestamp(date);
      date1.setDate(date1.getDate() + dayDuration);
      return this.getDateFromTimestamp(date1);
    },

    async getHomegroupLocations() {
      let resp = await this.$httpNoAuth.get("/api/v1/groups/meetings");
      let meetings = resp.data;
      resp = await this.$httpNoAuth.get("/api/v1/places/addresses");
      let addresses = resp.data;
      resp = await this.$httpNoAuth.get("/api/v1/groups/groups");
      let groups = resp.data;
      this.populateHomegroupData(meetings, addresses, groups);
    },

    populateHomegroupData(meetings, addresses, groups) {
      for (let m of meetings) {
        for (let a of addresses) {
          if (m.address_id === a.id) {
            for (let g of groups) {
              if (m.group_id === g.id) {
                this.homegroups.push({
                  position: {
                    lat: a.latitude,
                    lng: a.longitude
                  },
                  data: {
                    name: g.name,
                    description: g.description
                  },
                  opened: false
                });
              }
            }
          }
        }
      }
    }
  }
};
</script>
