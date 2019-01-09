<template>
  <v-layout align-center justify-end>
    <v-tooltip bottom>
      <v-btn flat icon slot="activator" v-bind:small="displayContext === 'compact'">
        <v-icon>edit</v-icon>
      </v-btn>
      <span>{{ $t("actions.edit") }}</span>
    </v-tooltip>
    <v-tooltip bottom>
      <v-btn flat icon slot="activator" v-bind:small="displayContext === 'compact'">
        <v-icon>delete</v-icon>
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
  }
}
</script>

<style>

</style>
