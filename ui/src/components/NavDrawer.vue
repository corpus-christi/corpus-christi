<template>
  <v-navigation-drawer app v-model="drawerVisible" width="200">
    <v-list>
      <template v-for="item in menuItems">
        <v-list-tile v-bind:key="item.route" v-bind:to="{ name: item.route }">
          <v-list-tile-action>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>{{ item.title }}</v-list-tile-title>
        </v-list-tile>
        <v-divider
          v-if="item.divider"
          v-bind:key="'div-' + item.route"
        ></v-divider>
      </template>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
export default {
  name: "NavDrawer",
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
          title: this.$t("events.title"),
          route: "events",
          icon: "event"
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
