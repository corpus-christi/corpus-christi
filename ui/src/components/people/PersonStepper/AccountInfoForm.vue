<template>
  <form>
    <v-text-field
      v-model="username"
      v-bind:label="$t('person.username') + ' *'"
      name="username"
      v-validate="{
        required: true,
        alpha_dash: true,
        min: 6,
      }"
      v-bind:error-messages="errors.collect('username')"
      prepend-icon="person"
      data-cy="username"
    />

    <!-- Password (new or update) -->
    <v-text-field
      v-model="password"
      type="password"
      ref="pwdField"
      v-bind:label="$t('person.password') + ' *'"
      name="password"
      v-validate="`${hasUsername}|min:8`"
      v-bind:error-messages="errors.collect('password')"
      prepend-icon="lock"
      data-cy="password"
    />
    <!-- Password confirmation (new or update) -->
    <v-text-field
      v-model="repeatPassword"
      type="password"
      v-bind:label="$t('person.repeat-password')"
      name="repeat-password"
      v-validate="`confirmed:pwdField|${hasUsername}`"
      v-bind:error-messages="errors.collect('repeat-password')"
      prepend-icon="lock"
      data-cy="confirm-password"
    />
  </form>
</template>

<script>
export default {
  name: "AccountInfoForm",
  data() {
    return {
      username: "",
      password: "",
      repeatPassword: "",
    };
  },
  computed: {
    hasUsername() {
      return this.username.length ? "required" : "";
    },
  },
};
</script>

<style scoped></style>
