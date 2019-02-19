<template>
  <v-navigation-drawer app v-model="drawerVisible">
    <v-list>
      <NavItem v-for="item in menuItems" :key="item.route" :item="item" />
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import NavItem from "./NavItem";

export default {
  name: "NavDrawer",
  components: {
    NavItem
  },
  data() {
    return {
      drawerVisible: false
    };
  },
  computed: {
    // Computed property so it's reactive.
    menuItems() {
      return [
        {
          title: this.$t("public.title"),
          route: "public",
          icon: "home",
          divider: true
        },
        {
          title: this.$t("people.title"),
          route: "people",
          icon: "account_circle"
        },
        {
          title: this.$t("groups.title"),
          route: "groups",
          icon: "group"
        },
        {
          title: this.$t("courses.course"),
          route: "courses",
          icon: "school",
          children: [
            {
              title: this.$t("diplomas.diploma"),
              route: "diplomas-admin"
            },
            {
              title: this.$t("transcripts.transcript"),
              route: "transcripts"
            }
          ]
        },
        {
          title: this.$t("events.header"),
          route: "events",
          icon: "event"
        },
        {
          title: this.$t("teams.title"),
          route: "teams",
          icon: "group"
        },
        {
          title: this.$t("assets.title"),
          route: "assets",
          icon: "devices_other"
        }
      ];
    }
  },
  methods: {
    toggle() {
      this.drawerVisible = !this.drawerVisible;
    }
  }
};
</script>
