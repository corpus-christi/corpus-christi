<template>
  <v-layout>
    <v-flex d-flex xs12 sm6 md4>
      <form>
        <v-text-field
          v-model="newAccount.firstName"
          v-bind:label="$t('label.name.first')"
          name="firstName"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('firstName')"
        ></v-text-field>

        <v-text-field
          v-model="newAccount.lastName"
          v-bind:label="$t('label.name.last')"
          name="lastName"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('lastName')"
        ></v-text-field>

        <v-radio-group v-model="newAccount.gender" row>
          <v-radio v-bind:label="$t('label.gender.male')" value="M"></v-radio>
          <v-radio v-bind:label="$t('label.gender.female')" value="F"></v-radio>
        </v-radio-group>

        <v-menu
          :close-on-content-click="false"
          v-model="showBirthdayPicker"
          :nudge-right="40"
          lazy
          transition="scale-transition"
          offset-y
          full-width
          min-width="290px"
        >
          <v-text-field
            slot="activator"
            v-model="newAccount.birthday"
            v-bind:label="$t('label.date.birthday')"
            prepend-icon="event"
            readonly
          ></v-text-field>

          <v-date-picker
            v-bind:locale="currentLanguageCode"
            v-model="newAccount.birthday"
            @input="showBirthdayPicker = false"
          ></v-date-picker>
        </v-menu>

        <v-text-field
          v-model="newAccount.email"
          v-bind:label="$t('label.email')"
          name="email"
          v-validate="'email'"
          v-bind:error-messages="errors.collect('email')"
          prepend-icon="email"
        ></v-text-field>

        <v-text-field
          v-model="newAccount.phone"
          v-bind:label="$t('label.phone')"
          prepend-icon="phone"
        ></v-text-field>

        <v-btn v-on:click="submit">Submit</v-btn>
        <v-btn v-on:click="clear">Clear</v-btn>
      </form>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapGetters } from "vuex";
export default {
  name: "PersonForm",
  data: function() {
    return {
      showBirthdayPicker: false,

      newAccount: {
        firstName: "",
        lastName: "",
        gender: "",
        birthdate: "",
        email: "",
        phone: ""
      }
    };
  },
  computed: mapGetters(["currentLanguageCode"]),
  methods: {
    submit() {
      this.$validator.validateAll();
      if (!this.errors.any()) {
        console.log("WOW");
      }
    },
    clear() {
      for (let key of Object.keys(this.newAccount)) {
        this.newAccount[key] = "";
      }
      this.$validator.reset();
    }
  }
};
</script>
