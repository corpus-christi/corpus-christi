<template>
  <div>
    <v-menu offset-y v-if="isLoggedIn">
      <template v-slot:activator="{ on }">
        <v-btn id="cur-locale" text v-on="on">
          {{ currentAccount.fullName() }}
          <v-icon>arrow_drop_down</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item v-on:click="logAccountOut" data-cy="logout">
          <v-list-item-title>
            {{ $t("actions.logout") }}
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <v-btn v-else text icon v-bind:to="{ name: 'login' }" data-cy="login">
      <v-icon>account_circle</v-icon>
    </v-btn>
  </div>
</template>

<script>
import { mapState, mapGetters, mapMutations } from "vuex";

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
