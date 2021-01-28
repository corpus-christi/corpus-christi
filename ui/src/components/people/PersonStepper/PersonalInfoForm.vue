<template>
  <form>
    <v-text-field
      v-model="firstName"
      v-bind:label="$t('person.name.first') + ' *'"
      name="firstName"
      v-validate="'required: true, regex:/[A-Za-zs\'-]$, max:64'"
      counter
      maxlength="64"
      v-bind:error-messages="errors.collect('firstName')"
      :readonly="formDisabled"
      data-cy="first-name"
    />

    <v-text-field
      v-model="lastName"
      v-bind:label="$t('person.name.last') + ' *'"
      name="lastName"
      v-validate="'required: true, regex:/[A-Za-z\s\'-]$/'"
      counter
      maxlength="64"
      v-bind:error-messages="errors.collect('lastName')"
      :readonly="formDisabled"
      data-cy="last-name"
    />

    <v-text-field
      v-model="secondLastName"
      v-bind:label="$t('person.name.second-last')"
      name="secondLastName"
      v-validate="'alpha_dash'"
      v-bind:error-messages="errors.collect('secondLastName')"
      counter
      maxlength="64"
      :readonly="formDisabled"
      data-cy="second-last-name"
    />

    <v-radio-group
      v-model="gender"
      :readonly="formDisabled"
      row
      data-cy="radio-gender"
    >
      <v-radio v-bind:label="$t('person.male')" value="M" />
      <v-radio v-bind:label="$t('person.female')" value="F" />
    </v-radio-group>

    <v-menu
      :close-on-content-click="false"
      v-model="showBirthdayPicker"
      :nudge-right="40"
      transition="scale-transition"
      offset-y
      min-width="290px"
      :disabled="formDisabled"
      data-cy="show-birthday-picker"
    >
      <template v-slot:activator="{ on }">
        <v-text-field
          slot="activator"
          v-model="birthday"
          name="birthday"
          v-bind:label="$t('person.date.birthday')"
          prepend-icon="event"
          readonly
          data-cy="birthday"
          data-vv-validate-on="input"
          v-validate="'date_format:yyyy-MM-dd'"
          v-bind:error-messages="errors.collect('birthday')"
          v-on="on"
        />
      </template>
      <v-date-picker
        v-bind:locale="currentLanguageCode"
        :max="getTodayString"
        v-model="birthday"
        @input="showBirthdayPicker = false"
        data-cy="birthday-picker"
      />
    </v-menu>

    <v-text-field
      v-model="email"
      v-bind:label="$t('person.email')"
      name="email"
      v-validate="'email'"
      data-vv-validate-on="change"
      v-bind:error-messages="errors.collect('email')"
      prepend-icon="email"
      data-cy="email"
      :readonly="formDisabled"
    />

    <v-text-field
      v-model="phone"
      v-bind:label="$t('person.phone')"
      prepend-icon="phone"
      data-cy="phone"
      :readonly="formDisabled"
    />
  </form>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  name: "PersonalInfoForm",
  data() {
    return {
      firstName: "",
      lastName: "",
      secondLastName: "",
      email: "",
      phone: "",
      gender: "",
      birthday: "",

      formDisabled: false,
      showBirthdayPicker: false,
    };
  },

  computed: {
    ...mapGetters(["currentLanguageCode"]),

    getTodayString() {
      let today = new Date();
      return `${today.getFullYear()}-${(today.getMonth() + 1).toLocaleString(
        "en-US",
        {
          minimumIntegerDigits: 2,
          useGrouping: false,
        }
      )}-${today.getDate().toLocaleString("en-US", {
        minimumIntegerDigits: 2,
        useGrouping: false,
      })}`;
    },
  },
};
</script>

<style scoped></style>
