<template>
  <form ref="form">
    <v-stepper v-model="currentStep" non-linear>
      <v-stepper-header>
        <v-stepper-step editable step="1">
          <span v-bind:class="{ 'red--text': stepOneErrors }">
            {{ $t("people.personal-information") }}
          </span>
        </v-stepper-step>

        <v-divider></v-divider>

        <v-stepper-step editable step="2" v-if="showAccountInfo">
          <span v-bind:class="{ 'red--text': stepTwoErrors }">
            {{ $t("people.account-information") }}
          </span>
          <small
            v-if="!isAccountRequired"
            v-bind:class="{ 'red--text': stepTwoErrors }"
            >{{ $t("people.optional") }}</small
          >
        </v-stepper-step>

        <v-divider></v-divider>

        <v-stepper-step editable v-bind:step="showAccountInfo ? 3 : 2">
          <span v-bind:class="{ 'red--text': stepThreeErrors }">
            {{ $t("people.additional-information") }}
          </span>
          <small v-bind:class="{ 'red--text': stepThreeErrors }">
            {{ $t("people.optional") }}
          </small>
        </v-stepper-step>
      </v-stepper-header>
      <v-stepper-items>
        <v-stepper-content step="1" class="formSteps">
          <v-text-field
            v-model="person.firstName"
            v-bind:label="$t('person.name.first') + ' *'"
            name="firstName"
            v-validate="'required|alpha_spaces'"
            v-bind:error-messages="errors.collect('firstName')"
            :readonly="formDisabled"
            data-cy="first-name"
          ></v-text-field>

          <v-text-field
            v-model="person.lastName"
            v-bind:label="$t('person.name.last') + ' *'"
            name="lastName"
            v-validate="'required|alpha_spaces'"
            v-bind:error-messages="errors.collect('lastName')"
            :readonly="formDisabled"
            data-cy="last-name"
          ></v-text-field>

          <v-text-field
            v-model="person.secondLastName"
            v-bind:label="$t('person.name.second-last')"
            name="secondLastName"
            v-validate="'alpha_spaces'"
            v-bind:error-messages="errors.collect('secondLastName')"
            :readonly="formDisabled"
            data-cy="second-last-name"
          ></v-text-field>

          <v-radio-group
            v-model="person.gender"
            :readonly="formDisabled"
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
            :disabled="formDisabled"
            data-cy="show-birthday-picker"
          >
            <v-text-field
              slot="activator"
              v-model="person.birthday"
              name="birthday"
              v-bind:label="$t('person.date.birthday')"
              prepend-icon="event"
              readonly
              data-cy="birthday"
              data-vv-validate-on="input"
              v-validate="'date_format:YYYY-MM-DD'"
              v-bind:error-messages="errors.collect('birthday')"
            ></v-text-field>
            <v-date-picker
              v-bind:locale="currentLanguageCode"
              :max="getTodayString"
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
            :readonly="formDisabled"
          ></v-text-field>
          <v-text-field
            v-model="person.phone"
            v-bind:label="$t('person.phone')"
            prepend-icon="phone"
            data-cy="phone"
            :readonly="formDisabled"
          ></v-text-field>
        </v-stepper-content>
        <v-stepper-content step="2" class="formSteps" v-if="showAccountInfo">
          <!-- User name (for creating new account) -->
          <v-text-field
            v-if="showAccountInfo"
            v-model="account.username"
            v-bind:label="
              $t('account.username') + (isAccountRequired ? ' *' : '')
            "
            name="username"
            v-validate="{
              required: isAccountRequired,
              alpha_dash: true,
              min: 6
            }"
            v-bind:error-messages="errors.collect('username')"
            prepend-icon="person"
            data-cy="username"
          ></v-text-field>

          <!-- Password (new or update) -->
          <v-text-field
            v-if="showAccountInfo"
            v-model="account.password"
            type="password"
            ref="pwdField"
            v-bind:label="
              $t('account.password') + (isAccountRequired ? ' *' : '')
            "
            name="password"
            v-validate="{ required: isAccountRequired, min: 8 }"
            v-bind:error-messages="errors.collect('password')"
            prepend-icon="lock"
            data-cy="password"
          ></v-text-field>
          <!-- Password confirmation (new or update) -->
          <v-text-field
            v-if="showAccountInfo"
            v-model="account.repeatPassword"
            type="password"
            v-bind:label="$t('account.repeat-password')"
            name="repeat-password"
            v-validate="'confirmed:pwdField'"
            v-bind:error-messages="errors.collect('repeat-password')"
            prepend-icon="lock"
            data-cy="confirm-password"
          ></v-text-field>
        </v-stepper-content>
        <v-stepper-content
          v-bind:step="showAccountInfo ? 3 : 2"
          class="formSteps"
        >
          <AttributeForm
            :personId="person.id"
            :existingAttributes="person.attributesInfo"
            v-model="attributeFormData"
            ref="attributeForm"
          ></AttributeForm>
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>
    <v-stepper v-model="currentStep">
      <v-stepper-content step="1">
        <v-layout row>
          <v-btn
            color="secondary"
            flat
            v-on:click="cancel"
            :disabled="formDisabled"
            data-cy="cancel"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn color="primary" raised v-on:click="next" data-cy="next">
            {{ $t("people.next") }}
          </v-btn>
        </v-layout>
      </v-stepper-content>
      <v-stepper-content step="2" v-if="showAccountInfo">
        <v-layout row>
          <v-btn
            color="secondary"
            flat
            v-on:click="cancel"
            :disabled="formDisabled"
            data-cy="cancel"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            raised
            v-on:click="previous"
            data-cy="previous"
            >{{ $t("people.previous") }}</v-btn
          >
          <v-btn color="primary" raised v-on:click="next" data-cy="next">
            {{ $t("people.next") }}
          </v-btn>
        </v-layout>
      </v-stepper-content>

      <v-stepper-content v-bind:step="showAccountInfo ? 3 : 2">
        <v-layout row>
          <v-btn
            color="secondary"
            flat
            v-on:click="cancel"
            :disabled="formDisabled"
            data-cy="cancel"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            outline
            v-on:click="addMore"
            v-if="addAnotherEnabled"
            :loading="addMoreIsLoading"
            :disabled="formDisabled"
            data-cy="add-another"
            >{{ $t("actions.add-another") }}</v-btn
          >
          <v-btn
            color="primary"
            raised
            v-on:click="previous"
            data-cy="previous"
            >{{ $t("people.previous") }}</v-btn
          >
          <v-btn
            color="primary"
            raised
            v-on:click="save"
            :loading="saveIsLoading"
            :disabled="formDisabled"
            data-cy="save"
            >{{ $t(saveButtonText) }}</v-btn
          >
        </v-layout>
      </v-stepper-content>
    </v-stepper>
  </form>
</template>

<script>
import { mapGetters } from "vuex";
import AttributeForm from "./input_fields/AttributeForm.vue";
import { isEmpty } from "lodash";

export default {
  name: "PersonForm",
  components: { AttributeForm },
  props: {
    initialData: {
      type: Object,
      required: true
    },
    addAnotherEnabled: {
      type: Boolean,
      required: false,
      default: false
    },
    saveButtonText: {
      type: String,
      required: false,
      default: "actions.save"
    },
    showAccountInfo: {
      type: Boolean,
      required: false,
      default: true
    },
    isAccountRequired: {
      type: Boolean,
      required: false,
      default: true
    }
  },
  data: function() {
    return {
      showBirthdayPicker: false,
      saveIsLoading: false,
      addMoreIsLoading: false,

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

      account: {
        username: "",
        password: "",
        repeatPassword: ""
      },

      attributeFormData: {},

      currentStep: 1,
      stepOneErrors: false,
      stepTwoErrors: false,
      stepThreeErrors: false
    };
  },
  computed: {
    // List the keys in a Person record.
    personKeys() {
      return Object.keys(this.person);
    },

    ...mapGetters(["currentLanguageCode"]),

    formDisabled() {
      return this.saveIsLoading || this.addMoreIsLoading;
    },

    getTodayString() {
      let today = new Date();
      let str = `${today.getFullYear()}-${(today.getMonth() + 1).toLocaleString(
        "en-US",
        { minimumIntegerDigits: 2, useGrouping: false }
      )}-${today.getDate().toLocaleString("en-US", {
        minimumIntegerDigits: 2,
        useGrouping: false
      })}`;
      return str;
    }
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
      this.stepOneErrors = false;
      this.stepTwoErrors = false;
      this.stepThreeErrors = false;
      this.resetForm();
      this.$emit("cancel");
    },

    // Clear the form and the validators.
    clear() {
      for (let key of this.personKeys) {
        this.person[key] = "";
      }
      this.$refs.attributeForm.clear();
      this.$validator.reset();
    },

    next() {
      this.setErrors();
      this.currentStep++;
    },

    previous() {
      this.setErrors();
      this.currentStep--;
    },

    redirectToErrors() {
      if (this.stepOneErrors) {
        this.currentStep = 1;
      } else if (this.stepTwoErrors) {
        this.currentStep = 2;
      } else if (this.stepThreeErrors) {
        this.currentStep = 3;
      }
    },

    resetForm() {
      this.saveIsLoading = false;
      this.addMoreIsLoading = false;
      this.currentStep = 1;
    },

    addMore() {
      this.addMoreIsLoading = true;
      this.savePerson("added-another");
    },

    save() {
      this.saveIsLoading = true;
      this.savePerson("saved");
    },

    setErrors() {
      this.stepOneErrors =
        this.errors.items.findIndex(element => {
          return (
            element.field == "firstName" ||
            element.field == "lastName" ||
            element.field == "secondLastName" ||
            element.field == "email" ||
            element.field == "brithday"
          );
        }) != -1;
      this.stepTwoErrors =
        this.errors.items.findIndex(element => {
          return (
            element.field == "username" ||
            element.field == "password" ||
            element.field == "confirm-password"
          );
        }) != -1;
      this.stepThreeErrors =
        this.errors.items.findIndex(element => {
          return (
            element.field != "username" &&
            element.field != "password" &&
            element.field != "confirm-password" &&
            element.field != "firstName" &&
            element.field != "lastName" &&
            element.field != "secondLastName" &&
            element.field != "email" &&
            element.field != "brithday"
          );
        }) != -1;
    },

    savePerson(emitMessage) {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          let attributes = [];
          let personId = this.person.id;
          for (let key in this.attributeFormData) {
            attributes.push(this.attributeFormData[key]);
          }
          delete this.person["attributesInfo"];
          delete this.person["accountInfo"];
          delete this.person["id"];
          let data = {
            person: this.person,
            attributesInfo: attributes
          };
          if (personId) {
            this.updatePerson(data, personId, emitMessage);
          } else {
            this.addPerson(data, emitMessage);
          }
        } else {
          this.setErrors();
          this.resetForm();
          this.redirectToErrors();
        }
      });
    },

    updatePerson(data, personId, emitMessage) {
      this.$http
        .put(`/api/v1/people/persons/${personId}`, data)
        .then(response => {
          this.$emit(emitMessage, response.data);
          this.resetForm();
          this.saveIsLoading = false;
        })
        .catch(err => {
          this.saveIsLoading = false;
          console.error("FALURE", err.response);
        });
    },

    addPerson(data, emitMessage) {
      this.$http
        .post("/api/v1/people/persons", data)
        .then(response => {
          if (this.account.username && this.account.password) {
            this.addAccount(response.data.id).then(() => {
              this.$emit(emitMessage, response.data);
              this.resetForm();
            });
          } else {
            this.$emit(emitMessage, response.data);
            this.resetForm();
          }
        })
        .catch(err => {
          this.resetForm();
          console.error("FAILURE", err.response);
        });
    },

    addAccount(personId) {
      return this.$http
        .post("/api/v1/people/accounts", {
          username: this.account.username,
          password: this.account.password,
          active: true,
          personId: personId
        })
        .then(resp => {
          console.log("ADDED", resp);
        })
        .catch(err => {
          this.resetForm();
          console.error("FAILURE", err.response);
        });
    }
  }
};
</script>
<style scoped>
.formSteps {
  height: 550px;
  overflow-y: scroll;
}
</style>
