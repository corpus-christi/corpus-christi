<template>
  <v-layout align-center justify-center column>
    <v-card-title class="headline">{{ $t("actions.signup") }}</v-card-title>
    <PersonForm
      v-bind:initialData="{}"
      v-bind:addAnotherEnabled="false"
      v-bind:saveButtonText="'actions.signup'"
      v-on:cancel="cancel"
      v-on:saved="save"
    />
  </v-layout>
</template>

<script>
import PersonForm from "./../components/people/PersonForm";

export default {
  name: "Signup",
  components: { PersonForm },
  methods: {
    cancel() {
      this.$router.go(-1);
    },

    save() {
      let routeName = this.$route.query.redirect || "login";
      this.$router.replace({ name: routeName });
    }
  }
};
</script>
