<template>
  <v-container>
    <v-col>
      <v-col cols="auto">
        <v-btn variant="outlined" color="primary" :to="{ path: '/events/all' }"
          ><v-icon>arrow_back</v-icon>{{ t("events.all-events") }}</v-btn
        >
      </v-col>
      <v-tabs color="transparent" slider-color="accent">
        <v-tab :to="{ path: '/event/' + eventId + '/details' }">
          <v-icon>list</v-icon>&nbsp;{{ t("events.details.title") }}
        </v-tab>
        <v-tab :to="{ path: '/event/' + eventId + '/participants' }">
          <v-icon>person</v-icon>&nbsp;{{ t("events.participants.title") }}
        </v-tab>
      </v-tabs>
      <hr class="vertical-spacer" />
      <router-view></router-view>
    </v-col>
  </v-container>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

const { t } = useI18n();
const route = useRoute();

const eventId = computed(() => route.params.event);
</script>

<style scoped>
.vertical-spacer {
  margin-bottom: 16px;
}
</style>
