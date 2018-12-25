<template>
  <v-snackbar v-model="show" v-bind:timeout="timeout">
    <slot></slot>
    <v-btn flat @click="$emit('close')"> {{ $t("actions.close") }} </v-btn>
  </v-snackbar>
</template>

<script>
export default {
  name: "Snackbar",
  props: {
    timeout: { type: Number, default: 5000 }
  },
  data() {
    return {
      show: false
    };
  }
};
</script>
