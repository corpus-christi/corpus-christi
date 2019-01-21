<template>
  <div>
    <v-menu offset-y v-if="isLoggedIn">
      <v-btn id="cur-locale" flat slot="activator">
        {{ currentAccount.fullName() }}
        <v-icon>arrow_drop_down</v-icon>
      </v-btn>

      <v-list>
        <v-list-tile v-on:click="logAccountOut" data-cy="logout">
          <v-list-tile-title> {{ $t("actions.logout") }} </v-list-tile-title>
        </v-list-tile>
      </v-list>
    </v-menu>

    <v-btn v-else flat icon v-bind:to="{ name: 'login' }" data-cy="login">
      <v-icon>account_circle</v-icon>
    </v-btn>
  </div>
</template>

<script>
import { mapMutations, mapGetters } from "vuex";

export default {
  name: "AccountMenu",

  computed: mapGetters(["isLoggedIn", "currentAccount"]),

  methods: {
    ...mapMutations(["logOut"]),

    logAccountOut() {
      this.logOut();
      this.$router.push({ name: "public" });
    }
  }
};
</script>
