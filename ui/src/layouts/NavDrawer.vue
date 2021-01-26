<template>
  <!-- Creates the Navigation Bar -->
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
/**
 * @file
 * @name NavDrawer.vue
 */
import NavItem from "./NavItem";
import { mapState } from "vuex";

/**
 * @module
 * @name NavDrawer
 * @exports ./app-bars/StandardAppBar.vue
 * Creates the Navigation Menu accessed by the hamburger button on the App Bar.
 */
export default {
  name: "NavDrawer",
  components: {
    NavItem,
  },
  props: ["value"],

  computed: {
    // Computed property so it's reactive.
    ...mapState(["currentAccount"]),
    menuItems: function () {
      if (this.currentAccount == null) {
        return [];
      } else {
        if (this.currentAccount.roles.includes("role.translator") === true) {
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
                  title: this.$t("courses.course"),
                  route: "courses",
                  isDropdown: true,
                },
                {
                  title: this.$t("diplomas.diploma"),
                  route: "diplomas-admin",
                  isDropdown: true,
                },
                {
                  title: this.$t("transcripts.transcript"),
                  route: "transcripts",
                  isDropdown: true,
                },
              ],
            },
            {
              title: this.$t("events.header"),
              route: "events",
              icon: "event",
              children: [
                {
                  title: this.$t("events.header"),
                  route: "all-events",
                  icon: "list",
                  isDropdown: true,
                },
                {
                  title: this.$t("events.calendar.title"),
                  route: "events-calendar",
                  icon: "date_range",
                  isDropdown: true,
                },
              ],
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
              title: this.$t("translation.menu-title"),
              route: "translation",
              icon: "library_books",
            },
          ];
        } else {
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
                  title: this.$t("courses.course"),
                  route: "courses",
                  isDropdown: true,
                },
                {
                  title: this.$t("diplomas.diploma"),
                  route: "diplomas-admin",
                  isDropdown: true,
                },
                {
                  title: this.$t("transcripts.transcript"),
                  route: "transcripts",
                  isDropdown: true,
                },
              ],
            },
            {
              title: this.$t("events.header"),
              route: "events",
              icon: "event",
              children: [
                {
                  title: this.$t("events.header"),
                  route: "all-events",
                  icon: "list",
                  isDropdown: true,
                },
                {
                  title: this.$t("events.calendar.title"),
                  route: "events-calendar",
                  icon: "date_range",
                  isDropdown: true,
                },
                {
                  title: this.$t("teams.title"),
                  route: "teams",
                  icon: "group",
                  isDropdown: true,
                },
                {
                  title: this.$t("assets.title"),
                  route: "assets",
                  icon: "devices_other",
                  isDropdown: true,
                },
              ],
            },
            {
              title: this.$t("places.title"),
              route: "places",
              icon: "places",
            },
          ];
        }
      }
    },
  },
};
</script>
