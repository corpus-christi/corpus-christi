<template>
  <div>
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
        :label="$t(attribute.name)"
        :name="$t(attribute.name)"
        :value="attribute.value"
      ></v-text-field>

      <v-date-picker
        :value="attribute.value"
        @input="
          showDatePicker = false;
          $emit('input', { stringValue: $event, enumValueId: 0 });
        "
      ></v-date-picker>
    </v-menu>
  </div>
</template>

<script>
export default {
  name: "Date",
  props: {
    attribute: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      showDatePicker: false
    };
  }
};
</script>
