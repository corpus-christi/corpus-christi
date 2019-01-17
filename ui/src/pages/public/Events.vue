<template>
  <v-container grid-list-md> 
    <v-layout layout row wrap>
      <v-flex xs12 sm6 md4 lg4 v-for="event in events" v-bind:key="event.id">
        <EventCard :event="event"></EventCard>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import EventCard from "../../components/public/EventCard";

export default {
  name: "Events",
  components: {
    EventCard
  },
  data() {
    return {
      events: [],
      pageLoaded: false
    };
  },
  mounted() {
    this.pageLoaded = false;
    this.$http.get(`/api/v1/events/?return_group=all&sort=start`).then(resp => {
      this.events = resp.data;
      console.log(resp.data);
      this.pageLoaded = true;
    });
  }
};
</script>

<style scoped></style>
