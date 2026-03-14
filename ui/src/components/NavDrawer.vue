<template>
  <v-navigation-drawer app v-model="drawerVisible">
    <v-list>
      <NavItem v-for="item in menuItems" :key="item.route" :item="item" />
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import NavItem from "./NavItem.vue";

const { t } = useI18n();
const drawerVisible = ref(false);

const menuItems = computed(() => [
  {
    title: t("public.title"),
    route: "public",
    icon: "home",
    divider: true
  },
  {
    title: t("people.title"),
    route: "people",
    icon: "account_circle"
  },
  {
    title: t("groups.title"),
    route: "groups",
    icon: "group"
  },
  {
    title: t("courses.course"),
    route: "courses",
    icon: "school",
    children: [
      {
        title: t("diplomas.diploma"),
        route: "diplomas-admin"
      },
      {
        title: t("transcripts.transcript"),
        route: "transcripts"
      }
    ]
  },
  {
    title: t("events.header"),
    route: "events",
    icon: "event"
  },
  {
    title: t("teams.title"),
    route: "teams",
    icon: "group"
  },
  {
    title: t("assets.title"),
    route: "assets",
    icon: "devices_other"
  },
  {
    title: t("places.title"),
    route: "places",
    icon: "places"
  }
]);

function toggle() {
  drawerVisible.value = !drawerVisible.value;
}

defineExpose({ toggle });
</script>
