<template>
    <v-toolbar class="pa-1">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("places.title") }}</v-toolbar-title>
        </v-flex>
        <v-flex md2>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            single-line
            hide-details
            data-cy="form-search"
          ></v-text-field>
        </v-flex>
        <v-flex md3>
          <v-select
            hide-details
            solo
            single-line
            :items="viewOptions"
            v-model="viewStatus"
            data-cy="view-status-select"
          >
          </v-select>
        </v-flex>
        <v-flex shrink justify-self-end>
          <v-btn
            color="primary"
            raised
            v-on:click.stop="newAsset"
            data-cy="add-asset"
          >
            <v-icon dark left>add</v-icon>
            {{ $t("places.new") }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-toolbar>





</template>

<script>
    export default {
    name: "PlacesTable.vue"
    }
</script>

<style scoped>

</style>
