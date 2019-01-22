<template>
  <v-layout align-center justify-end>
    <v-tooltip bottom v-if="!student.confirmed">
      <v-btn
        flat
        icon
        outline
        color="primary"
        slot="activator"
        v-bind:small="displayContext === 'compact'"
        @click="emitAction('confirm')"
      >
        <v-icon v-bind:small="displayContext === 'compact'">done</v-icon>
      </v-btn>
      <span>{{ $t("actions.confirm") }}</span>
    </v-tooltip>
    <v-tooltip bottom>
      <v-btn
        flat
        icon
        outline
        color="primary"
        slot="activator"
        v-bind:small="displayContext === 'compact'"
        @click="emitAction(student.active ? 'deactivate' : 'activate')"
      >
        <v-icon v-bind:small="displayContext === 'compact'">
          {{ student.active ? "archive" : "undo" }}
        </v-icon>
      </v-btn>
      <span>{{
        $t(
          student.active
            ? "actions.tooltips.archive"
            : "actions.tooltips.unarchive"
        )
      }}</span>
    </v-tooltip>
  </v-layout>
</template>

<script>
export default {
  props: {
    student: Object,
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
