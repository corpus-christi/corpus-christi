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
        v-on:click.stop="emitAction('edit')"
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
        @click.stop="emitAction(diploma.active ? 'deactivate' : 'activate')"
      >
        <v-icon v-bind:small="displayContext === 'compact'">
          {{ diploma.active ? "archive" : "undo" }}
        </v-icon>
      </v-btn>
      <span>{{
        $t(
          diploma.active
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
    diploma: Object,
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
