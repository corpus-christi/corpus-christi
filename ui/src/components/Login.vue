<template>
  <v-container fluid fill-height>
    <v-layout align-center justify-center>
      <v-flex xs12 sm8 md6>
        <v-card class="elevation-12">
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{ $t("home.login.header") }}</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-toolbar>
          <v-card-text>
            <v-form>
              <v-text-field
                v-model="username"
                v-bind:label="$t('person.username')"
                prepend-icon="person"
                name="login"
                type="text"
              ></v-text-field>
              <v-text-field
                v-model="password"
                v-bind:label="$t('person.password')"
                prepend-icon="lock"
                name="password"
                type="password"
              ></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" v-on:click="login">
              {{ $t("actions.login") }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapMutations } from "vuex";
import Account from "../models/Account";

export default {
  name: "Login",
  data() {
    return {
      username: "",
      password: ""
    };
  },
  methods: {
    async login() {
      const jwt_resp = await this.$http.post("/login", {
        username: this.username,
        password: this.password
      });
      if (jwt_resp.status !== 200) {
        console.error(`JWT STATUS ${jwt_resp.status}`);
        return;
      }
      this.setCurrentJWT(jwt_resp.data.jwt);

      const account_resp = await this.$http.get(
        `/api/v1/people/accounts/username/${this.username}`
      );
      if (account_resp.status !== 200) {
        console.error(`ACCT STATUS ${account_resp.status}`);
        return;
      }

      console.log("ACCT", account_resp);

      const person_resp = await this.$http.get(
        `/api/v1/people/persons/${account_resp.data.personId}`
      );
      if (person_resp.status !== 200) {
        console.error(`PERSON STATUS ${person_resp.status}`);
        return;
      }

      this.setCurrentAccount(
        new Account(
          this.username,
          person_resp.data.firstName,
          person_resp.data.lastName
        )
      );
    },

    ...mapMutations(["setCurrentAccount", "setCurrentJWT"])
  }
};
</script>
