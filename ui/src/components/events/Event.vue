<template>
  <v-container>
    <v-layout column>
      <v-flex shrink>
        <v-btn outline color="primary" :to="{ path: '/events/all' }"
          ><v-icon>arrow_back</v-icon>{{ $t("events.all-events") }}</v-btn
        >
      </v-flex>
      <v-tabs color="transparent" slider-color="accent">
        <v-tab ripple :to="{ path: '/event/' + eventId + '/details' }">
          <v-icon>list</v-icon>&nbsp;{{ $t("events.details.title") }}
        </v-tab>
        <v-tab ripple :to="{ path: '/event/' + eventId + '/participants' }">
          <v-icon>person</v-icon>&nbsp;{{ $t("events.participants.title") }}
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
    }
  },

  data() {
    return {
      activeTab: null,
      currentPath: this.$route.path,
      currentComponent: "details",
      tabs: {
        details: 0,
        participants: 1,
        assets: 2
      }
    };
  }
};
</script>

<style scoped>
.vertical-spacer {
  margin-bottom: 16px;
}
</style>
