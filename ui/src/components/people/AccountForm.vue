<template>
  <v-card>
    <!-- Title -->
    <v-card-title>
      <h3 class="headline">
        {{ $t("person.settings", { person: this.fullName }) }}
      </h3>
    </v-card-title>
    <div v-if="!rolesEnabled">
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
          v-validate="'required|min:8'"
          data-vv-validate-on="change"
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
          v-validate="'confirmed:pwdField|required'"
          v-bind:error-messages="errors.collect('repeat-password')"
          prepend-icon="lock"
          data-cy="confirm-password"
        ></v-text-field>
      </v-card-text>
    </div>
    <div v-if="rolesEnabled">
      <v-card-title>{{ $t("person.actions.assign-roles") }}</v-card-title>
      <v-card-text>
        <v-select
          v-model="currentRoles"
          :items="translatedRoles"
          v-bind:label="$t('person.account-info.roles')"
          chips
          deletable-chips
          clearable
          outline
          multiple
          hide-selected
          return-object
          item-value="value"
          item-text="text"
          :menu-props="{ closeOnContentClick: true }"
          data-cy="account-form-roles"
        >
        </v-select>
      </v-card-text>
    </div>
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
    account: { type: Object, required: true },
    rolesList: Array,
    rolesEnabled: {
      type: Boolean,
      required: false
    }
  },
  data() {
    return {
      username: "",
      password: "",
      repeat_password: "",
      currentRoles: [],
      snackbar: {
        show: false,
        text: ""
      }
    };
  },
  watch: {
    person(new_person) {
      if (isEmpty(new_person)) {
        this.clear();
      } else {
        this.clearForm(new_person);
      }
    }
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
    },
    translatedRoles() {
      return this.rolesList.map(element => {
        return {
          text: this.$t(element.text),
          value: element.value
        };
      });
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
            var roles = [];
            for (var role of this.currentRoles) {
              if (role.value) {
                roles.push(role.value);
              } else {
                roles.push(role);
              }
            }
            if (this.rolesEnabled) {
              this.$emit("updateAccount", this.account.id, { roles: roles });
            } else {
              this.$emit("updateAccount", this.account.id, {
                password: this.password
              });
            }
          }
          this.close();
        }
      });
    },
    clearForm(new_person) {
      this.username = this.password = this.repeat_password = "";
      if (this.person.accountInfo) {
        this.currentRoles = [];
        for (var role of new_person.accountInfo.roles) {
          this.currentRoles.push(role.id);
        }
      }
    },
    deactivateAccount() {
      this.$emit("deactivateAccount", this.account.id);
      this.close();
    },
    reactivateAccount() {
      this.$emit("reactivateAccount", this.account.id);
      this.close();
    },
    close() {
      this.$validator.reset();
      this.clearForm(this.person);
      this.$emit("close");
    }
  }
};
</script>
