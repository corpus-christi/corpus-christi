<template>
  <v-container>
    <v-layout row>
      <v-flex xs12 sm6 md5>
        <v-card>
          <v-toolbar color="cyan" dark>
            <v-toolbar-title>
              {{ $t("home.headers.upcoming-classes") }}
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
        <v-toolbar color="blue" dark>
          <v-toolbar-title>
            {{ $t("home.headers.upcoming-events") }}
          </v-toolbar-title>
        </v-toolbar>
        <v-list>
          <v-card v-for="(item, idx) in events" v-bind:key="idx">
            <v-card-title>
              <div>
                <span>{{ item.title }}</span> <br />
                <span class="grey--text">
                  {{ item.startDate }}
                  <span v-if="item.endDate">to {{ item.endDate }}</span>
                </span>
              </div>
            </v-card-title>
            <v-card-text>{{ item.description }}</v-card-text>
            <v-divider></v-divider>
          </v-card>
        </v-list>
      </v-flex>
    </v-layout>

    <v-layout>
      <v-flex>
        <v-toolbar color="blue" dark>
          <v-toolbar-title>
            {{ $t("home.headers.home-church") }}
          </v-toolbar-title>
        </v-toolbar>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  name: "Home",
  data() {
    return {
      classes: [
        { title: "Intro to New Testament", date: "2019-01-03" },
        { title: "Christian Parenting 1", date: "2019-01-12" },
        { title: "Christian Parenting 2", date: "2019-01-19" }
      ],
      events: [
        {
          title: "Men's Retreat",
          startDate: "2019-03-15",
          endDate: "2019-03-17",
          description: "Longer description of the men's retreat."
        },
        {
          title: "Family Fun Day",
          startDate: "2019-04-10",
          description: "All the cool stuff happening on family fun day."
        }
      ]
    };
  }
};
</script>
