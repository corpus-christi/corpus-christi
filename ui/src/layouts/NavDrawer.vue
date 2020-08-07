<template>
  <v-navigation-drawer
    app
    clipped
    v-bind:value="value"
    v-on:input="$emit('input', $event)"
  >
    <v-list>
      <nav-item v-for="item in menuItems" :key="item.route" :item="item" />
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import NavItem from "./NavItem";

export default {
  name: "NavDrawer",
  components: {
    NavItem,
  },
  props: ["value"],

  computed: {
    // Computed property so it's reactive.
    menuItems: function () {
      return [
        {
          title: this.$t("public.title"),
          route: "public",
          icon: "home",
          divider: true,
        },
        {
          title: this.$t("people.title"),
          route: "people",
          icon: "account_circle",
        },
        {
          title: this.$t("groups.title"),
          route: "groups",
          icon: "group",
        },
        {
          title: this.$t("courses.course"),
          route: "courses",
          icon: "school",
          children: [
            {
              title: this.$t("diplomas.diploma"),
              route: "diplomas-admin",
            },
            {
              title: this.$t("transcripts.transcript"),
              route: "transcripts",
            },
          ],
        },
        {
          title: this.$t("events.header"),
          route: "events",
          icon: "event",
        },
        {
          title: this.$t("teams.title"),
          route: "teams",
          icon: "group",
        },
        {
          title: this.$t("assets.title"),
          route: "assets",
          icon: "devices_other",
        },
        {
          title: this.$t("places.title"),
          route: "places",
          icon: "places",
        },
        {
          title: "Translation(Need)",
          route: "translation",
          icon: "library_books",
        },
      ];
    },
  },
};
</script>
