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
        <div v-if="hasAttributes">
          <span class="headline">{{ $t("people.attributes") }}</span>
          <AttributeForm
            :attributes="attributeFields"
            v-model="formData"
          ></AttributeForm>
        </div>
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
import { isEmpty, find } from "lodash";
import AttributeForm from "./input-fields/AttributeForm.vue";

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
    },
    attributes: {
      type: Array,
      required: true
    },
    translations: {
      type: Object,
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
      formData: {}
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
    },

    hasAttributes() {
      return this.$props.attributes.length !== 0;
    },

    getTodayString() {
      let today = new Date();
      let str = `${today.getFullYear()}-${
        (today.getMonth() + 1).toLocaleString("en-US",
          { minimumIntegerDigits: 2, useGrouping: false })}-${
        today.getDate().toLocaleString("en-US", 
          { minimumIntegerDigits: 2, useGrouping: false })}`;

      console.log(str);
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
      this.constructAttributeForm(this.$props.attributes);
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
      this.constructAttributeForm(this.$props.attributes);
      this.$validator.reset();
    },

    // Trigger a save event, returning the update `Person`.
    save() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.person.attributesInfo = this.collectAttributes();
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
    },

    collectAttributes() {
      let attributes = [];
      for (let attribute of this.attributeFields) {
        attributes.push({
          personId: this.person.id ? this.person.id : 0,
          attributeId: attribute.id,
          enumValueId: this.isEnum(attribute.fieldType)
            ? this.formData[attribute.id]
            : 0,
          stringValue: this.isEnum(attribute.fieldType)
            ? ""
            : this.formData[attribute.id].toString()
        });
      }
      return attributes;
    },

    isEnum(type) {
      return type === "Dropdown" || type === "Radio";
    },

    getExistingAttribute(attributeId) {
      let existingValue = find(this.person.attributesInfo, item => {
        return item.attributeId === attributeId;
      });
      return existingValue
        ? existingValue
        : { stringValue: "", enumValueId: 0 };
    },

    constructAttributeForm(attributes) {
      attributes.sort((a, b) => {
        return a.seq - b.seq;
      });
      this.attributeFields = [];
      // reference: https://blog.rangle.io/how-to-create-data-driven-user-interfaces-in-vue/
      for (let attr of attributes) {
        let component;
        switch (attr.typeI18n) {
          case "attribute.float":
            component = this.floatFieldConstructor(attr);
            break;
          case "attribute.integer":
            component = this.integerFieldConstructor(attr);
            break;
          case "attribute.date":
            component = this.dateFieldConstructor(attr);
            break;
          case "attribute.string":
            component = this.stringFieldConstructor(attr);
            break;
          case "attribute.dropdown":
            component = this.dropdownFieldConstructor(attr);
            break;
          case "attribute.check":
            component = this.checkFieldConstructor(attr);
            break;
          case "attribute.radio":
            component = this.radioFieldConstructor(attr);
            break;
        }
        this.attributeFields.push(component);
      }
    },

    floatFieldConstructor(attr) {
      this.$set(
        this.formData,
        attr.id.toString(),
        this.getExistingAttribute(attr.id).stringValue
      );
      return {
        fieldType: "Float",
        name: this.translations[attr.nameI18n],
        label: this.translations[attr.nameI18n],
        id: attr.id.toString()
      };
    },

    integerFieldConstructor(attr) {
      this.$set(
        this.formData,
        attr.id.toString(),
        this.getExistingAttribute(attr.id).stringValue
      );
      return {
        fieldType: "Integer",
        name: this.translations[attr.nameI18n],
        label: this.translations[attr.nameI18n],
        id: attr.id.toString()
      };
    },

    dateFieldConstructor(attr) {
      this.$set(
        this.formData,
        attr.id.toString(),
        this.getExistingAttribute(attr.id).stringValue
      );
      return {
        fieldType: "Date",
        name: this.translations[attr.nameI18n],
        label: this.translations[attr.nameI18n],
        id: attr.id.toString()
      };
    },

    stringFieldConstructor(attr) {
      this.$set(
        this.formData,
        attr.id.toString(),
        this.getExistingAttribute(attr.id).stringValue
      );
      return {
        fieldType: "String",
        name: this.translations[attr.nameI18n],
        label: this.translations[attr.nameI18n],
        id: attr.id.toString()
      };
    },

    dropdownFieldConstructor(attr) {
      let options = [];
      for (let item of attr.enumerated_values) {
        options.push({
          text: this.translations[item.valueI18n],
          value: item.id
        });
      }

      this.$set(
        this.formData,
        attr.id.toString(),
        this.getExistingAttribute(attr.id).enumValueId
      );
      return {
        fieldType: "Dropdown",
        name: this.translations[attr.nameI18n],
        label: this.translations[attr.nameI18n],
        options: options,
        id: attr.id.toString()
      };
    },

    checkFieldConstructor(attr) {
      let options = [];
      for (let item of attr.enumerated_values) {
        options.push({
          label: this.translations[item.valueI18n],
          name: this.translations[item.valueI18n],
          value: item.id
        });
      }

      let existingAttr = this.getExistingAttribute(attr.id).stringValue.split(
        ","
      );
      for (let index in existingAttr) {
        existingAttr[index] = Number(existingAttr[index]);
      }

      this.$set(this.formData, attr.id.toString(), existingAttr);
      return {
        fieldType: "Check",
        name: this.translations[attr.nameI18n],
        label: this.translations[attr.nameI18n],
        options: options,
        value: existingAttr,
        id: attr.id.toString()
      };
    },

    radioFieldConstructor(attr) {
      let options = [];
      for (let item of attr.enumerated_values) {
        options.push({
          label: this.translations[item.valueI18n],
          name: this.translations[item.valueI18n],
          value: item.id,
          inputValue: this.getExistingAttribute(attr.id).enumValueId
        });
      }

      this.$set(
        this.formData,
        attr.id.toString(),
        this.getExistingAttribute(attr.id).enumValueId
      );
      return {
        fieldType: "Radio",
        name: this.translations[attr.nameI18n],
        label: this.translations[attr.nameI18n],
        options: options,
        id: attr.id.toString()
      };
    }
  }
};
</script>
