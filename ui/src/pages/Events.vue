<template>
  <v-container>
    <v-tabs color="transparent" slider-color="accent">
      <v-tab ripple :to="{ path: '/events/all' }">
        <v-icon>event</v-icon>&nbsp;{{ $t("events.header") }}
      </v-tab>
      <v-tab ripple :to="{ path: '/events/calendar' }">
        <v-icon>date_range</v-icon>&nbsp;{{ $t("events.calendar.title") }}
      </v-tab>
    </v-tabs>
    <hr class="vertical-spacer" />
    <v-container> <router-view></router-view> </v-container>
  </v-container>
</template>

<script>
export default {
  name: "Events"
};
</script>
