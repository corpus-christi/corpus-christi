<template>
  <v-menu
    :close-on-content-click="false"
    v-model="showDatePicker"
    :nudge-right="40"
    lazy
    transition="scale-transition"
    offset-y
    full-width
    min-width="290px"
  >
    <v-text-field
      slot="activator"
      prepend-icon="event"
      readonly
      :label="label"
      :name="name"
      :value="value"
    ></v-text-field>

    <v-date-picker
      :value="value"
      @input="showDatePicker = false; $emit('input', $event)"
    ></v-date-picker>
  </v-menu>
</template>

<script>
export default {
  name: "Date",
  props: {
    label: {
      type: String,
      required: true
    },
    name: {
      type: String,
      required: true
    },
    value: {
      type: String,
      required: true
    }
  },
  data: () => {
    return {
      showDatePicker: false,
    };
  }
};
</script>
