<template>
  <v-container fluid fill-height>
    <v-layout align-center justify-center>
      <v-flex xs12 sm8 md6>
        <v-card class="elevation-12">
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{ $t("login.header") }}</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-toolbar>
          <v-card-text>
            <v-form>
              <v-text-field
                v-model="username"
                v-bind:label="$t('account.username')"
                prepend-icon="person"
                name="login"
                type="text"
              ></v-text-field>
              <v-text-field
                v-model="password"
                v-bind:label="$t('account.password')"
                prepend-icon="lock"
                name="password"
                type="password"
              ></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" v-on:click="cancel">
              {{ $t("actions.cancel") }}
            </v-btn>
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
    ...mapMutations(["logIn"]),

    cancel() {
      this.$router.push({ name: "public" });
    },

    async login() {
      const resp = await this.$http.post("/api/v1/auth/login", {
        username: this.username,
        password: this.password
      });
      if (resp.status !== 200) {
        console.error(`JWT STATUS ${resp.status}`);
        return;
      }

      this.logIn({
        account: new Account(
          resp.data.username,
          resp.data.firstName,
          resp.data.lastName
        ),
        jwt: resp.data.jwt
      });

      // Normally want to use `push`, but unlikely that
      // the user wants to return to the login page.
      const routeName = this.$route.query.redirect || "admin";
      this.$router.replace({ name: routeName });
    }
  }
};
</script>
