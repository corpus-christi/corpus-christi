<template>
  <v-card>
    <!-- Title -->
    <v-card-title>
      <h3 class="headline">
        {{ t("person.settings", { person: fullName }) }}
      </h3>
    </v-card-title>
    <div v-if="!rolesEnabled">
      <v-card-title> {{ title }} </v-card-title>
      <v-card-text>
        <!-- User name (for creating new account) -->
        <v-text-field
          v-if="addingAccount"
          v-model="username"
          v-bind:label="t('person.username')"
          name="username"
          prepend-icon="person"
          data-cy="new-account-username"
        ></v-text-field>

        <!-- Password (new or update) -->
        <v-text-field
          v-model="password"
          type="password"
          ref="pwdField"
          v-bind:label="t('person.password')"
          name="password"
          prepend-icon="lock"
          data-cy="new-update-password"
        ></v-text-field>
        <!-- Password confirmation (new or update) -->
        <v-text-field
          v-model="repeat_password"
          type="password"
          v-bind:label="t('person.repeat-password')"
          name="repeat-password"
          prepend-icon="lock"
          data-cy="confirm-password"
        ></v-text-field>
      </v-card-text>
    </div>
    <div v-if="rolesEnabled">
      <v-card-title>{{ t("person.actions.assign-roles") }}</v-card-title>
      <v-card-text>
        <v-select
          v-model="currentRoles"
          :items="translatedRoles"
          v-bind:label="t('person.account-info.roles')"
          chips
          closable-chips
          clearable
          multiple
          hide-selected
          return-object
          item-value="value"
          item-title="title"
          :menu-props="{ closeOnContentClick: true }"
          data-cy="account-form-roles"
        >
        </v-select>
      </v-card-text>
    </div>
    <v-card-actions>
      <v-spacer v-if="!person.accountInfo"></v-spacer>
      <v-btn color="secondary" variant="text" v-on:click="close" data-cy="cancel-button">
        {{ t("actions.cancel") }}
      </v-btn>
      <v-spacer v-if="person.accountInfo"></v-spacer>
      <v-btn
        v-if="person.active && person.accountInfo && account.active"
        color="primary"
        variant="outlined"
        v-on:click="deactivateAccount"
        data-cy="deactivate-account"
      >
        {{ t("actions.deactivate-account") }}
      </v-btn>
      <v-btn
        v-if="person.active && person.accountInfo && !account.active"
        color="primary"
        variant="outlined"
        v-on:click="reactivateAccount"
        data-cy="reactivate-account"
      >
        {{ t("actions.activate-account") }}
      </v-btn>
      <v-btn
        color="primary"
        variant="elevated"
        v-on:click="confirm"
        data-cy="confirm-button"
      >
        {{ t("actions.confirm") }}
      </v-btn>
    </v-card-actions>

    <v-snackbar v-model="snackbar.show"> {{ snackbar.text }} </v-snackbar>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { isEmpty } from "lodash";

const { t } = useI18n();

const props = defineProps<{
  person: any;
  account?: any;
  rolesList?: any[];
  rolesEnabled?: boolean;
}>();

const emit = defineEmits(["addAccount", "updateAccount", "deactivateAccount", "reactivateAccount", "close"]);

const username = ref("");
const password = ref("");
const repeat_password = ref("");
const currentRoles = ref<any[]>([]);
const snackbar = ref({ show: false, text: "" });

const addingAccount = computed(() => isEmpty(props.account));

const fullName = computed(() => `${props.person.firstName} ${props.person.lastName}`);

const title = computed(() =>
  addingAccount.value
    ? t("person.actions.add-account")
    : t("person.actions.reset-password")
);

const translatedRoles = computed(() => {
  if (!props.rolesList) return [];
  return props.rolesList.map(element => ({
    title: t(element.text),
    value: element.value
  }));
});

watch(
  () => props.person,
  (new_person) => {
    if (isEmpty(new_person)) {
      clearFields();
    } else {
      clearForm(new_person);
    }
  }
);

function clearFields() {
  username.value = "";
  password.value = "";
  repeat_password.value = "";
  currentRoles.value = [];
}

function clearForm(new_person: any) {
  username.value = "";
  password.value = "";
  repeat_password.value = "";
  if (props.person.active) {
    currentRoles.value = [];
    for (const role of new_person.roles || []) {
      currentRoles.value.push(role.id);
    }
  }
}

function confirm() {
  if (addingAccount.value) {
    emit("addAccount", {
      username: username.value,
      password: password.value,
      active: true,
      personId: props.person.id
    });
  } else {
    const roles: any[] = [];
    for (const role of currentRoles.value) {
      if (role.value) {
        roles.push(role.value);
      } else {
        roles.push(role);
      }
    }
    if (props.rolesEnabled) {
      emit("updateAccount", props.person.id, { roles: roles });
    } else {
      emit("updateAccount", props.person.id, { password: password.value });
    }
  }
  close();
}

function deactivateAccount() {
  emit("deactivateAccount", props.account.id);
  close();
}

function reactivateAccount() {
  emit("reactivateAccount", props.account.id);
  close();
}

function close() {
  clearForm(props.person);
  emit("close");
}
</script>
