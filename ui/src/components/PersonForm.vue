<template>
  <div>
    <h2>{{ $t("message.hello") }}</h2>
    <v-form v-model="valid">
      <v-text-field
        v-model="newAccount.firstName"
        v-bind:label="$t('label.name.first')"
        name="firstName"
        v-validate="'required|max:3'"
        v-bind:error-messages="errors.collect('firstName')"
      ></v-text-field>
      <v-text-field
        v-model="newAccount.lastName"
        v-bind:label="$t('label.name.last')"
        name="lastName"
        v-validate="'min:5'"
        v-bind:error-messages="errors.collect('lastName')"
      ></v-text-field>
      <v-btn v-bind:disabled="!valid" v-on:click="handleSubmit">Sign Up</v-btn>
    </v-form>
  </div>
</template>

<script>
export default {
  name: "PersonForm",
  data: function() {
    return {
      valid: false, // Are all the fields in the form valid?

      newAccount: {
        // Object to collect together account data
        firstName: "",
        lastName: ""
      }
    };
  },

  mounted() {
    // this.$validator.localize("en");
  },
  methods: {
    handleSubmit: () => {}
  }
};
</script>
