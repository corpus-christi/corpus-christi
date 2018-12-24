<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ $t("person.actions.new") }}</span>
    </v-card-title>
    <v-card-text>
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
      </form>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" flat v-on:click="cancel">
        {{ $t("actions.cancel") }}
      </v-btn>
      <v-btn color="primary" flat v-on:click="clear">
        {{ $t("actions.clear") }}
      </v-btn>
      <v-btn color="primary" flat v-on:click="save">
        {{ $t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mapGetters } from "vuex";

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
    cancel() {
      this.$emit("cancel");
    },
    clear() {
      for (let key of Object.keys(this.newPerson)) {
        this.newPerson[key] = "";
      }
      this.$validator.reset();
    },
    save() {
      this.$validator.validateAll();
      if (!this.errors.any()) {
        this.$emit("save", this.newPerson);
      }
    }
  }
};
</script>
