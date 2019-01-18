<template>
  <v-card>
    {{ formData }}
    <v-card-title>
      <span class="headline">{{ $t("actions.signup") }}</span>
    </v-card-title>
    <v-card-text>
      <form ref="form">
        <v-text-field
          v-model="person.firstName"
          v-bind:label="$t('person.name.first')"
          name="firstName"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('firstName')"
          :readonly="isLoading"
          data-cy="first-name"
        ></v-text-field>

        <v-text-field
          v-model="person.lastName"
          v-bind:label="$t('person.name.last')"
          name="lastName"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('lastName')"
          :readonly="isLoading"
          data-cy="last-name"
        ></v-text-field>

        <v-text-field
          v-model="person.secondLastName"
          v-bind:label="$t('person.name.second-last')"
          name="secondLastName"
          v-bind:error-messages="errors.collect('secondLastName')"
          :readonly="isLoading"
          data-cy="second-last-name"
        ></v-text-field>

        <v-radio-group
          v-model="person.gender"
          :readonly="isLoading"
          row
          data-cy="radio-gender"
        >
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
          :disabled="isLoading"
          data-cy="show-birthday-picker"
        >
          <v-text-field
            slot="activator"
            v-model="person.birthday"
            v-bind:label="$t('person.date.birthday')"
            prepend-icon="event"
            readonly
            data-cy="birthday"
          ></v-text-field>

          <v-date-picker
            v-bind:locale="currentLanguageCode"
            v-model="person.birthday"
            @input="showBirthdayPicker = false"
            data-cy="birthday-picker"
          ></v-date-picker>
        </v-menu>

        <v-text-field
          v-model="person.email"
          v-bind:label="$t('person.email')"
          name="email"
          v-validate="'email'"
          data-vv-validate-on="change"
          v-bind:error-messages="errors.collect('email')"
          prepend-icon="email"
          data-cy="email"
          :readonly="isLoading"
        ></v-text-field>

        <v-text-field
          v-model="person.phone"
          v-bind:label="$t('person.phone')"
          prepend-icon="phone"
          data-cy="phone"
          :readonly="isLoading"
        ></v-text-field>
        <AttributeForm v-model="formData"></AttributeForm>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        flat
        v-on:click="clear"
        :disabled="isLoading"
        data-cy="clear"
        >{{ $t("actions.clear") }}</v-btn
      >
      <v-btn
        color="secondary"
        flat
        v-on:click="signup"
        :disabled="isLoading"
        data-cy="signup"
        >{{ $t("actions.signup") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
import { mapGetters } from "vuex";
import AttributeForm from "./input-fields/AttributeForm.vue";

export default {
  name: "NewAccountForm",
  components: { AttributeForm },
  props: {},
  data: function() {
    return {
      showBirthdayPicker: false,
      isLoading: false,

      person: {
        id: 0,
        active: true,
        firstName: "",
        lastName: "",
        secondLastName: "",
        gender: "",
        birthday: "",
        email: "",
        phone: "",
        locationId: 0,
        attributesInfo: []
      },

      attributeFields: [],
      formData: {},
      translations: {},
      attributes: []
    };
  },
  computed: {
    // List the keys in a Person record.
    personKeys() {
      return Object.keys(this.person);
    },

    ...mapGetters(["currentLanguageCode"])
  },
  methods: {
    // Clear the form and the validators.
    clear() {
      for (let key of this.personKeys) {
        this.person[key] = "";
      }
      this.$validator.reset();
    },

    // Trigger a save event, returning the update `Person`.
    signup() {
      this.isLoading = true;
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.person.attributesInfo = this.collectAttributes();
          this.$emit("save", this.person);
        } else {
          this.isLoading = false;
        }
      });
    }
  }
};
</script>
