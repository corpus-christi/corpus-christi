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
            v-model="date"
            @input="$emit('input', $event)"
            v-validate="'date_format:YYYY-MM-DD'"
          ></v-text-field>

          <v-date-picker
            v-model="date"
            @input="showDatePicker = false"
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
    }
  },
  data: () => {
    return {
      showDatePicker: false,
      date: ""
    }
  }
};
</script>
