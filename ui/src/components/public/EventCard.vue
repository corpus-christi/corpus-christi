<template>
  <v-card class="card elevation-10">    
    <v-card-title>
      <v-layout row align-center justify-center>
        <v-flex shrink>
          <span class="headline mb-3">{{ event.title }}</span>
        </v-flex>
      </v-layout>      
    </v-card-title>

    <v-card-text class="text">
      <v-layout>
        <v-flex>
          <div><b>Start: </b>{{ getDisplayDate(event.start) }}</div>
          <div class="mb-3"><b>End: </b>{{ getDisplayDate(event.end) }}</div>
          <div class="mb-3">{{ event.description }}</div>
        </v-flex>
      </v-layout>
    </v-card-text>

    <v-card-actions>
      <v-spacer></v-spacer>
        <v-btn raised color="primary">Join Event</v-btn>
      <v-spacer></v-spacer>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: "EventCard",
  props: {
    event: {}
  },
  data() {
    return {

    };
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
    }
  }
};
</script>

<style scoped>

.text {
  max-height: 200px;
  min-height: 200px;
}

.card {
  margin: 25px;
  padding: 10px;
  border-radius: 30px;
}

</style>
