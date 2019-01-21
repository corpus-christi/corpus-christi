<template>
  <v-card>
    <PersonForm
      v-bind:initialData="{}"
      v-bind:title="$t('actions.signup')"
      v-bind:addAnotherEnabled="false"
      v-bind:saveButtonText="'actions.signup'"
    />
  </v-card>
</template>

<script>
import PersonForm from "./../components/people/PersonForm";

export default {
  name: "Signup",
  components: { PersonForm }
};
</script>
