<template>
  <v-card class="card elevation-10">
    <!-- Image -->
    <template v-if="event.images.length > 0">
      <v-img
        class="picture"
        :src="'/api/v1/images/' + event.images[0].image.id"
      >
      </v-img>
    </template>

    <!-- Placeholder if no image uploaded -->
    <template v-else>
      <v-img class="picture" :src="arcoPlaceholder"> </v-img>
    </template>
    <v-divider></v-divider>
    <div class="body">
      <v-card-title>
        <v-row align="center" justify="center">
          <v-col shrink>
            <span class="headline mb-3">{{ event.title }}</span>
          </v-col>
        </v-row>
      </v-card-title>

      <v-card-text class="text">
        <v-row>
          <v-col>
            <div v-if="event.location">
              <b>{{ t("events.location") }}: </b
              >{{ event.location.description }}
            </div>
            <div>
              <b>{{ t("events.start-time") }}: </b
              >{{ getDisplayDate(event.start) }}
            </div>
            <div class="mb-3">
              <b>{{ t("events.end-time") }}: </b
              >{{ getDisplayDate(event.end) }}
            </div>
            <div class="mb-3">{{ event.description }}</div>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn variant="elevated" rounded color="primary">{{
          t("public.events.join")
        }}</v-btn>
        <v-spacer></v-spacer>
      </v-card-actions>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useAuthStore } from "@/stores/auth";
import arcoPlaceholder from "../../../assets/arco-placeholder.jpg";

const { t } = useI18n();
const authStore = useAuthStore();

const props = defineProps<{
  event: any;
}>();

function getDisplayDate(ts: string) {
  let date = new Date(ts);
  return date.toLocaleTimeString(authStore.currentLanguageCode, {
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}
</script>

<style scoped>
.picture {
  max-height: 200px;
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
