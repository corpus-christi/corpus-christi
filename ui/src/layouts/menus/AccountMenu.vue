<template>
  <div>
    <!-- If logged in, display a button the User's full name. -->
    <v-menu offset-y v-if="isLoggedIn">
      <template v-slot:activator="{ on }">
        <v-btn id="cur-locale" text v-on="on">
          {{ currentAccount.fullName() }}
          <v-icon>arrow_drop_down</v-icon>
        </v-btn>
      </template>

      <!-- If the button is clicked, show a dropdown with a logout button. -->
      <v-list>
        <v-list-item v-on:click="logAccountOut" data-cy="logout">
          <v-list-item-title>
            {{ $t("actions.logout") }}
          </v-list-item-title>
        </v-list-item>
      </v-list>
      -->
    </v-menu>

    <!-- If not logged in, displays an "account circle" icon. -->
    <v-btn v-else text icon v-bind:to="{ name: 'login' }" data-cy="login">
      <v-icon>account_circle</v-icon>
    </v-btn>
  </div>
</template>

<script>
/**
 * @file
 * @name AccountMenu.vue
 */
import { mapState, mapGetters, mapMutations } from "vuex";

/**
 * @module
 * @name AccountMenu
 * @exports ../app-bars/StandardAppBar
 * The Login/Logout button on the App Bar.
 */
export default {
  name: "AccountMenu",

  computed: {
    ...mapState(["currentAccount"]),
    ...mapGetters(["isLoggedIn"]),
  },

  methods: {
    ...mapMutations(["logOut"]),

    logAccountOut() {
      this.logOut();
      this.$router.push({ name: "public" });
    },
  },
};
</script>
