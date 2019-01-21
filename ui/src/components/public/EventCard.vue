<template>
  <v-card class="card elevation-10">
    <!-- TODO: Replace with actual event image -->
    <v-img
      v-if="event.image"
      src="https://i.ytimg.com/vi/LQ1ZMvqlqYA/maxresdefault.jpg"
      class="image"
    >
    </v-img>
    <!-- Placeholder for if they don't add images -->
    <v-img
      v-else
      src="https://i.ytimg.com/vi/LQ1ZMvqlqYA/maxresdefault.jpg"
      class="image"
    >
    </v-img>
    <v-divider></v-divider>
    <div class="body">
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
            <div v-if="event.location">
              <b>{{ $t("events.location") }}: </b
              >{{ event.location.description }}
            </div>
            <div>
              <b>{{ $t("events.start-time") }}: </b
              >{{ getDisplayDate(event.start) }}
            </div>
            <div class="mb-3">
              <b>{{ $t("events.end-time") }}: </b
              >{{ getDisplayDate(event.end) }}
            </div>
            <div class="mb-3">{{ event.description }}</div>
          </v-flex>
        </v-layout>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn raised color="primary">{{ $t("public.events.join") }}</v-btn>
        <v-spacer></v-spacer>
      </v-card-actions>
    </div>
  </v-card>
</template>

<script>
export default {
  name: "EventCard",
  props: {
    event: {}
  },
  data() {
    return {};
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
.image {
  max-height: 300px;
  min-height: 200px;
}

.text {
  max-height: 200px;
  min-height: 200px;
}

.card {
  margin: 25px;
  border-radius: 30px;
}

.body {
  padding-top: 10px;
  border-radius: 30px;
}
</style>
