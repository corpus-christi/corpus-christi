<template>
  <v-card>
    <PersonForm
      v-bind:initialData="{}"
      v-bind:title="$t('actions.signup')"
      v-bind:addAnotherEnabled="false"
      v-bind:saveButtonText="'actions.signup'"
      v-on:cancel="cancel"
      v-on:saved="save"
    />
  </v-card>
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
