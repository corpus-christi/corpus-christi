<template>
  <form>
    <v-text-field
      v-model="newPerson.firstName"
      v-bind:label="$t('person.name.first')"
      name="firstName"
      v-validate="'required'"
      v-bind:error-messages="errors.collect('firstName')"
    ></v-text-field>

    <v-text-field
      v-model="newPerson.lastName"
      v-bind:label="$t('person.name.last')"
      name="lastName"
      v-validate="'required'"
      v-bind:error-messages="errors.collect('lastName')"
    ></v-text-field>

    <v-radio-group v-model="newPerson.gender" row>
      <v-radio v-bind:label="$t('person.male')" value="M"></v-radio>
      <v-radio v-bind:label="$t('person.female')" value="F"></v-radio>
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
        v-model="newPerson.birthday"
        v-bind:label="$t('person.date.birthday')"
        prepend-icon="event"
        readonly
      ></v-text-field>

      <v-date-picker
        v-bind:locale="currentLanguageCode"
        v-model="newPerson.birthday"
        @input="showBirthdayPicker = false"
      ></v-date-picker>
    </v-menu>

    <v-text-field
      v-model="newPerson.email"
      v-bind:label="$t('person.email')"
      name="email"
      v-validate="'email'"
      v-bind:error-messages="errors.collect('email')"
      prepend-icon="email"
    ></v-text-field>

    <v-text-field
      v-model="newPerson.phone"
      v-bind:label="$t('person.phone')"
      prepend-icon="phone"
    ></v-text-field>

    <v-btn v-on:click="submit">Submit</v-btn>
    <v-btn v-on:click="clear">Clear</v-btn>
  </form>
</template>

<script>
import { mapGetters } from "vuex";
import axios from "axios";

export default {
  name: "PersonForm",
  data: function() {
    return {
      showBirthdayPicker: false,

      newPerson: {
        firstName: "",
        lastName: "",
        gender: "",
        birthday: "",
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
        axios
          .post("/api/v1/people/persons", this.newPerson)
          .then(resp => console.log("SUCCESS", resp))
          .catch(err => console.error("FAILURE", err.response));
      }
    },
    clear() {
      for (let key of Object.keys(this.newPerson)) {
        this.newPerson[key] = "";
      }
      this.$validator.reset();
    }
  }
};
</script>
