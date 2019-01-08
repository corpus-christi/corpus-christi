<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-text-field
          v-model="person.firstName"
          v-bind:label="$t('person.name.first')"
          name="firstName"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('firstName')"
        ></v-text-field>

        <v-text-field
          v-model="person.lastName"
          v-bind:label="$t('person.name.last')"
          name="lastName"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('lastName')"
        ></v-text-field>

        <v-radio-group v-model="person.gender" row>
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
            v-model="person.birthday"
            v-bind:label="$t('person.date.birthday')"
            prepend-icon="event"
            readonly
          ></v-text-field>

          <v-date-picker
            v-bind:locale="currentLanguageCode"
            v-model="person.birthday"
            @input="showBirthdayPicker = false"
          ></v-date-picker>
        </v-menu>

        <v-text-field
          v-model="person.email"
          v-bind:label="$t('person.email')"
          name="email"
          v-validate="'email'"
          v-bind:error-messages="errors.collect('email')"
          prepend-icon="email"
        ></v-text-field>

        <v-text-field
          v-model="person.phone"
          v-bind:label="$t('person.phone')"
          prepend-icon="phone"
        ></v-text-field>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" flat v-on:click="cancel">{{
        $t("actions.cancel")
      }}</v-btn>
      <v-btn color="primary" flat v-on:click="clear">{{
        $t("actions.clear")
      }}</v-btn>
      <v-btn color="primary" flat v-on:click="save">{{
        $t("actions.save")
      }}</v-btn>
      <v-btn color="primary" flat v-on:click="add_another">{{
        $t("actions.addanother")
      }}</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mapGetters } from "vuex";
import { isEmpty } from "lodash";

export default {
  name: "PersonForm",
  props: {
    editMode: {
      type: Boolean,
      required: true
    },
    initialData: {
      type: Object,
      required: true
    }
  },
  data: function() {
    return {
      showBirthdayPicker: false,

      person: {
        firstName: "",
        lastName: "",
        gender: "",
        birthday: "",
        email: "",
        phone: ""
      }
    };
  },
  computed: {
    // List the keys in a Person record.
    personKeys() {
      return Object.keys(this.person);
    },

    title() {
      return this.editMode
        ? this.$t("person.actions.edit")
        : this.$t("person.actions.new");
    },

    ...mapGetters(["currentLanguageCode"])
  },

  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(personProp) {
      if (isEmpty(personProp)) {
        this.clear();
      } else {
        this.person = personProp;
      }
    }
  },

  methods: {
    // Abandon ship.
    cancel() {
      this.clear();
      this.$emit("cancel");
    },

    // Clear the form and the validators.
    clear() {
      for (let key of this.personKeys) {
        this.person[key] = "";
      }
      this.$validator.reset();
    },

    // Trigger a save event, returning the update `Person`.
    save() {
      this.$validator.validateAll();
      if (!this.errors.any()) {
        this.$emit("save", this.person);
      }
    },

    add_another() {
      this.$validator.validateAll();
      if (!this.errors.any()) {
        this.$emit("add-another", this.person);
      }
    }
  }
};
</script>
