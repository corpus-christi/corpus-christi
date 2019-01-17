<template>
  <v-card>
    <!-- Title -->
    <v-card-title>
      <h3 class="headline">
        {{ $t("person.settings", { person: this.fullName }) }}
      </h3>
    </v-card-title>

    <v-card-title> {{ title }} </v-card-title>
    <v-card-text>
      <!-- User name (for creating new account) -->
      <v-text-field
        v-if="addingAccount"
        v-model="username"
        v-bind:label="$t('account.username')"
        name="username"
        v-validate="'required|alpha_dash|min:6'"
        v-bind:error-messages="errors.collect('username')"
        prepend-icon="person"
        data-cy="new-account-username"
      ></v-text-field>

      <!-- Password (new or update) -->
      <v-text-field
        v-model="password"
        type="password"
        ref="pwdField"
        v-bind:label="$t('account.password')"
        name="password"
        v-validate="'min:8'"
        v-bind:error-messages="errors.collect('password')"
        prepend-icon="lock"
        data-cy="new-update-password"
      ></v-text-field>
      <!-- Password confirmation (new or update) -->
      <v-text-field
        v-model="repeat_password"
        type="password"
        v-bind:label="$t('account.repeat-password')"
        name="repeat-password"
        v-validate="'confirmed:pwdField'"
        v-bind:error-messages="errors.collect('repeat-password')"
        prepend-icon="lock"
        data-cy="confirm-password"
      ></v-text-field>
    </v-card-text>

    <v-card-actions>
      <v-spacer v-if="!person.accountInfo"></v-spacer>
      <v-btn color="secondary" flat v-on:click="close" data-cy="cancel-button">
        {{ $t("actions.cancel") }}
      </v-btn>
      <v-spacer v-if="person.accountInfo"></v-spacer>
      <v-btn
        v-if="person.active && person.accountInfo && account.active"
        color="primary"
        outline
        v-on:click="deactivateAccount"
        data-cy="deactivate-account"
      >
        {{ $t("actions.deactivate-account") }}
      </v-btn>
      <v-btn
        v-if="person.active && person.accountInfo && !account.active"
        color="primary"
        outline
        v-on:click="reactivateAccount"
        data-cy="reactivate-account"
      >
        {{ $t("actions.activate-account") }}
      </v-btn>
      <v-btn
        color="primary"
        raised
        v-on:click="confirm"
        data-cy="confirm-button"
      >
        {{ $t("actions.confirm") }}
      </v-btn>
    </v-card-actions>

    <v-snackbar v-model="snackbar.show"> {{ snackbar.text }} </v-snackbar>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";

export default {
  name: "AccountForm",
  props: {
    person: { type: Object, required: true },
    account: { type: Object, required: true }
  },
  data() {
    return {
      username: "",
      password: "",
      repeat_password: "",

      snackbar: {
        show: false,
        text: ""
      }
    };
  },
  computed: {
    // Are we adding an account (vs. updating an existing one)?
    addingAccount() {
      return isEmpty(this.account);
    },

    fullName() {
      return `${this.person.firstName} ${this.person.lastName}`;
    },

    title() {
      return this.addingAccount
        ? this.$t("person.actions.add-account")
        : this.$t("person.actions.reset-password");
    }
  },
  methods: {
    confirm() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          if (this.addingAccount) {
            this.$emit("addAccount", {
              username: this.username,
              password: this.password,
              active: true,
              personId: this.person.id
            });
          } else {
            this.$emit("updateAccount", this.account.id, {
              password: this.password
            });
          }
          this.close();
        }
      });
    },
    deactivateAccount() {
      console.log(this.account.id);
      this.$emit("deactivateAccount", this.account.id);
      this.close();
    },
    reactivateAccount() {
      console.log(this.account.id);
      this.$emit("reactivateAccount", this.account.id);
      this.close();
    },
    close() {
      this.$validator.reset();
      this.username = this.password = this.repeat_password = "";
      this.$emit("close");
    }
  }
};
</script>
