<template>
  <v-layout align-center justify-end>
    <v-tooltip bottom>
      <v-btn
        flat
        icon
        outline
        color="primary"
        slot="activator"
        v-bind:small="displayContext === 'compact'"
        @click="emitAction('edit')"
      >
        <v-icon v-bind:small="displayContext === 'compact'">edit</v-icon>
      </v-btn>
      <span>{{ $t("actions.edit") }}</span>
    </v-tooltip>
    <v-tooltip bottom>
<<<<<<< HEAD
      <v-btn flat icon
        color="primary"
        slot="activator"
        v-bind:small="displayContext === 'compact'"
        @click="emitAction('deactivate')">

          <v-icon v-bind:small="displayContext === 'compact'">remove_circle</v-icon>
=======
      <v-btn
        flat
        icon
        outline
        color="primary"
        slot="activator"
        v-bind:small="displayContext === 'compact'"
        @click="emitAction('deactivate')"
      >
        <v-icon v-bind:small="displayContext === 'compact'">
          {{ course.active ? "archive" : "unarchive" }}
        </v-icon>
>>>>>>> c89e2f3398750f806c7deb60596fbb9b2814d9ee
      </v-btn>
      <span>{{ $t("actions.tooltips.deactivate") }}</span>
    </v-tooltip>
  </v-layout>
</template>

<script>
export default {
  props: {
    course: Object,
    displayContext: String
  },
  methods: {
    emitAction(actionName) {
      this.$emit("action", actionName);
    }
  }
};
</script>

<style></style>
