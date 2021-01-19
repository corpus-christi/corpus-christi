<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>{{ $t("assets.title") }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="$t('actions.search')"
        single-line
        hide-details
      ></v-text-field>
    </v-toolbar>
  </div>
</template>

<script>
  export default {
    name: "EventAssets",
    computed: {

    },

    data() {
      return {
        search: "",
      }
    },
  }
</script>