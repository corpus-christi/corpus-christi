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
        data-cy="edit"
      >
        <v-icon v-bind:small="displayContext === 'compact'">edit</v-icon>
      </v-btn>
      <span>{{ $t("actions.edit") }}</span>
    </v-tooltip>
    <v-tooltip bottom>
      <v-btn
        flat
        icon
        outline
        color="primary"
        slot="activator"
        v-bind:small="displayContext === 'compact'"
        @click="emitAction(course.active ? 'deactivate' : 'activate')"
        data-cy="archive-toggle"
      >
        <v-icon v-bind:small="displayContext === 'compact'">
          {{ course.active ? "archive" : "undo" }}
        </v-icon>
      </v-btn>
      <span>{{
        $t(
          course.active
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
