<template>
  <v-container>
    <v-tabs color="primary" slider-color="accent" fixed-tabs>
      <!-- Links to /events/all. -->
      <v-tab ripple :to="{ path: '/events/all' }">
        <v-icon>event</v-icon>&nbsp;{{ $t("events.header") }}
      </v-tab>
      <!-- Links to /events/calendar. -->
      <v-tab ripple :to="{ path: '/events/calendar' }">
        <v-icon>date_range</v-icon>&nbsp;{{ $t("events.calendar.title") }}
      </v-tab>
    </v-tabs>
    <hr class="vertical-spacer" />
    <v-container> <router-view></router-view> </v-container>
  </v-container>
</template>

<script>
/**
 * @file
 * @name Events.vue
 */

/**
 * @module
 * @name Events
 * @exports ../router.js
 * Draws the base webpage for /events. Page functionality stored in ui/src/components/events
 */
export default {
  name: "Events",
};
</script>
