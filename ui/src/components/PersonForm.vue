<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form ref="form">
        <v-text-field
          v-model="person.firstName"
          v-bind:label="$t('person.name.first')"
          name="firstName"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('firstName')"
          :readonly="formDisabled"
          data-cy="first-name"
        ></v-text-field>

        <v-text-field
          v-model="person.lastName"
          v-bind:label="$t('person.name.last')"
          name="lastName"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('lastName')"
          :readonly="formDisabled"
          data-cy="last-name"
        ></v-text-field>

        <v-text-field
          v-model="person.secondLastName"
          v-bind:label="$t('person.name.second-last')"
          name="secondLastName"
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
          :readonly="formDisabled"
        ></v-text-field>

        <v-text-field
          v-model="person.phone"
          v-bind:label="$t('person.phone')"
          prepend-icon="phone"
          data-cy="phone"
          :readonly="formDisabled"
        ></v-text-field>
        <AttributeForm
          :personId="person.id"
          :existingAttributes="person.attributesInfo"
          v-model="attributeFormData"
          ref="attributeForm"
        ></AttributeForm>
      </form>
    </v-card-text>
    <v-card-actions>
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
        flat
        v-on:click="clear"
        :disabled="formDisabled"
        data-cy="clear"
        >{{ $t("actions.clear") }}</v-btn
      >
      <v-btn
        color="primary"
        outline
        v-on:click="add_another"
        v-if="editMode === false"
        :loading="addMoreLoading"
        :disabled="formDisabled"
        data-cy="add-another"
        >{{ $t("actions.add-another") }}</v-btn
      >
      <v-btn
        color="primary"
        raised
        v-on:click="save"
        :loading="saveLoading"
        :disabled="formDisabled"
        data-cy="save"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
import { mapGetters } from "vuex";
import AttributeForm from "./input-fields/AttributeForm.vue";
import { isEmpty } from "lodash";

export default {
  name: "PersonForm",
  components: { AttributeForm },
  props: {
    editMode: {
      type: Boolean,
      required: true
    },
    initialData: {
      type: Object,
      required: true
    },
    addMoreLoading: {
      type: Boolean,
      required: true
    },
    saveLoading: {
      type: Boolean,
      required: true
    }
  },
  data: function() {
    return {
      showBirthdayPicker: false,

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
      attributeFormData: {}
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

    ...mapGetters(["currentLanguageCode"]),

    formDisabled() {
      return this.saveLoading || this.addMoreLoading;
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

    // Trigger a save event, returning the update `Person`.
    save() {
      console.log("SAVING");
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.$set(this.person, "attributesInfo", this.attributeFormData);
          console.log(this.person.attributesInfo);
          console.log(this.attributeFormData);
          this.$emit("save", this.person);
        }
      });
    },

    add_another() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.$emit("add-another", this.person);
        }
      });
    }
  }
};
</script>
