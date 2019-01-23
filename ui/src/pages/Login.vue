<template>
  <div>
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
                  v-on:keyup.enter="login"
                  data-cy="username"
                ></v-text-field>
                <v-text-field
                  v-model="password"
                  v-bind:label="$t('account.password')"
                  prepend-icon="lock"
                  name="password"
                  type="password"
                  v-on:keyup.enter="login"
                  data-cy="password"
                ></v-text-field>
              </v-form>
              <v-flex>
                {{ $t("account.no-account") }}
                <router-link v-bind:to="{ name: 'signup' }" data-cy="signup">
                  <a class="href" v-text="$t('actions.signup')" />
                </router-link>
              </v-flex>
            </v-card-text>
            <v-card-actions>
              <v-layout fill-height justify-end align-end column xs12>
                <v-flex>
                  <v-btn flat v-on:click="cancel" data-cy="cancel">{{
                    $t("actions.cancel")
                  }}</v-btn>
                  <v-btn color="primary" v-on:click="login" data-cy="login">{{
                    $t("actions.login")
                  }}</v-btn>
                </v-flex>
              </v-layout>
            </v-card-actions>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false" data-cy>
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import { mapMutations } from "vuex";
import Account from "../models/Account";

export default {
  name: "Login",
  data() {
    return {
      username: "",
      password: "",

      snackbar: {
        show: false,
        text: ""
      }
    };
  },
  methods: {
    ...mapMutations(["logIn"]),

    cancel() {
      this.$router.push({ name: "public" });
    },

    async login() {
      try {
        const resp = await this.$httpNoAuth.post("/api/v1/auth/login", {
          username: this.username,
          password: this.password
        });
        if (resp.status !== 200) {
          console.error(`JWT STATUS ${resp.status}`);
          return;
        } else {
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
      } catch (err) {
        console.log(err);
        this.snackbar.text = this.$t("login.messages.incorrect-login");
        this.snackbar.show = true;
      }
    }
  }
};
</script>
