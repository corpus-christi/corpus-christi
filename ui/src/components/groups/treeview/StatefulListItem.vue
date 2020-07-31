<template>
  <!-- this component wraps the v-list-item component with a checkbox,
    providing a two-way sync to the specified set of data 
    the checkbox's state will be set according to the "state" prop.
    the component will emit a "changed" event on click, with a boolean
    indicating the desired change value of the "state" prop.
  -->
  <v-list-item @click="$emit('changed', !state)" v-bind="attrs">
    <v-list-item-icon v-if="icon"><v-icon v-text="icon" /></v-list-item-icon>
    <v-list-item-content>
      <v-list-item-title>{{ text }}</v-list-item-title>
    </v-list-item-content>
    <v-list-item-action>
      <v-checkbox
        :input-value="state"
        :indeterminate="state === null"
      ></v-checkbox>
    </v-list-item-action>
  </v-list-item>
</template>
<script>
export default {
  name: "StatefulListItem",
  props: {
    state: {
      /* indicate the state of the checkbox.
        null: indeterminate
        true: checked
        false: unchecked
      */
      type: Boolean,
      default: false,
    },
    text: {
      /* the title text for the list item */
      type: String,
      required: true,
    },
    icon: {
      /* icon to add to the list item */
      type: String,
    },
    attrs: {
      /* attributes to apply to the list item */
      type: Object,
    },
  },
};
</script>
