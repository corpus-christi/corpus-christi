<template>
  <v-container>
    <v-layout row>
      <v-flex xs12 sm6 md5>
        <v-card>
          <v-toolbar color="cyan" dark>
            <v-toolbar-title>
              {{ $t("public.headers.upcoming-classes") }}
            </v-toolbar-title>
          </v-toolbar>
          <v-list>
            <template v-for="(item, idx) in classes">
              <v-list-tile avatar v-bind:key="idx">
                <v-list-tile-avatar>
                  <v-icon>calendar_today</v-icon>
                </v-list-tile-avatar>
                <v-list-tile-content>
                  <v-list-tile-title>{{ item.title }}</v-list-tile-title>
                  <v-list-tile-sub-title>{{ item.date }}</v-list-tile-sub-title>
                </v-list-tile-content>
              </v-list-tile>
              <v-divider
                v-if="idx + 1 < classes.length"
                v-bind:key="'div' + idx"
              ></v-divider>
            </template>
          </v-list>
        </v-card>
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
import GoogleMap from "../components/public/GoogleMap";
export default {
  name: "Public",
  components: { GoogleMap },
  data() {
    return {
      classes: [
        { title: "Intro to New Testament", date: "2019-01-03" },
        { title: "Christian Parenting 1", date: "2019-01-12" },
        { title: "Christian Parenting 2", date: "2019-01-19" }
      ],
      events: [],
      homegroups: [],
      pageLoaded: false
    };
  },
  mounted() {
    this.pageLoaded = false;
    this.$http.get(`/api/v1/events/?return_group=all`).then(resp => {
      this.events = resp.data;
      this.events = this.events.slice(0, 5);
      console.log(resp.data);
      this.pageLoaded = true;
    });

    this.getHomegroupLocations();
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
