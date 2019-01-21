<template>
  <v-card>
    <v-card-title>Register for this course</v-card-title>
    <v-card-text>
      <v-form>
        <v-text-field
          v-model="username"
          v-bind:label="$t('account.username')"
          prepend-icon="person"
          type="text"
          data-cy="username"
        ></v-text-field>
        <v-text-field
          v-model="password"
          v-bind:label="$t('account.password')"
          prepend-icon="lock"
          name="password"
          type="password"
          data-cy="password"
        ></v-text-field>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" v-on:click="cancel" data-cy="cancel">{{ $t("actions.cancel") }}</v-btn>
      <v-btn color="primary" v-on:click="register" data-cy="register">{{ $t("actions.login") }}</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: "courseRegistrationForm",
  data() {
    return {
      username: "",
      password: ""
    };
  },
  props: {
  },

  methods: {
    cancel() {
      this.clear();
      this.$emit("cancel");
    },
    register() {

    },
    clear() {
      
    }
  }
};
</script>

<style>
</style>
