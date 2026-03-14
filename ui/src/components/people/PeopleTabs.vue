<template>
  <div>
    <v-tabs v-model="activeTab" color="transparent" slider-color="accent">
      <v-tab
        v-on:click="router.push({ path: '/events/' + route.params.event + '/details' })"
      >
        <v-icon>list</v-icon>&nbsp;{{ t("events.details.title") }}
      </v-tab>
      <v-tab
        v-on:click="router.push({ path: '/events/' + route.params.event + '/participants' })"
      >
        <v-icon>person </v-icon>&nbsp;{{ t("events.participants.title") }}
      </v-tab>
      <v-tab
        v-on:click="router.push({ path: '/events/' + route.params.event + '/teams' })"
      >
        <v-icon>group</v-icon>&nbsp;{{ t("events.teams.title") }}
      </v-tab>
      <v-tab
        v-on:click="router.push({ path: '/events/' + route.params.event + '/assets' })"
      >
        <v-icon>devices_other</v-icon>&nbsp;{{ t("events.assets.title") }}
      </v-tab>
    </v-tabs>
    <hr class="vertical-spacer" />
    <router-view></router-view>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter, useRoute } from "vue-router";

const { t } = useI18n();
const router = useRouter();
const route = useRoute();

const activeTab = ref<any>(null);
const currentComponent = ref("details");
const tabs: Record<string, number> = {
  details: 0,
  participants: 1,
  teams: 2,
  assets: 3
};

function updateActiveTab(fullPath: string) {
  const splitPath = fullPath.split("/");
  currentComponent.value = splitPath[splitPath.length - 1];
  activeTab.value = tabs[currentComponent.value];
}

watch(route, (to) => {
  updateActiveTab(to.fullPath);
});

onMounted(() => {
  updateActiveTab(route.fullPath);
});
</script>

<style scoped>
.vertical-spacer {
  margin-bottom: 16px;
}
</style>
