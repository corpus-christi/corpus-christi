<template>
  <v-container>
    <v-layout column>
      <v-flex shrink>
        <v-btn outlined color="primary" :to="{ path: '/events/all' }"
          ><v-icon>arrow_back</v-icon>{{ $t("events.all-events") }}</v-btn
        >
      </v-flex>
      <v-tabs color="primary" slider-color="accent" fixed-tabs>
        <v-tab ripple :to="{ path: '/event/' + eventId + '/details' }">
          <v-icon left>list</v-icon>{{ $t("events.details.title") }}
        </v-tab>
        <v-tab ripple :to="{ path: '/event/' + eventId + '/participants' }">
          <v-icon left>person</v-icon>{{ $t("events.participants.title") }}
        </v-tab>
        <v-tab ripple :to="{ path: '/event/' + eventId + '/assets' }">
          <v-icon left>devices_other</v-icon>{{ $t("assets.title") }}
        </v-tab>
      </v-tabs>
      <hr class="vertical-spacer" />
      <router-view></router-view>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  name: "Event",
  computed: {
    eventId() {
      return this.$route.params.event;
    },
  },

  data() {
    return {
      activeTab: null,
      currentPath: this.$route.path,
      currentComponent: "details",
      tabs: {
        details: 0,
        participants: 1,
        assets: 2,
      },
    };
  },
};
</script>

<style scoped>
.vertical-spacer {
  margin-bottom: 16px;
}
</style>
