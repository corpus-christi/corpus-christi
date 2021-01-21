<template>
  <v-card
    class="mr-2"
    outlined
    elevation="2"
    v-if="true"
  >
    <v-row
      class="subrow"
      align="center"
      no-gutters
    >
      <v-col
        align="center"
      >
        <v-btn
          class="ml-3"
          dark
          
        >
          Add New Locale
        </v-btn>
      </v-col>
      <v-col
        class="ml-5"
        align="center"
      >
        <v-btn
          dark
          @click="$emit('goToBot')"
        >
          <v-icon>keyboard_arrow_down</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row
      class="subrow"
      no-gutters
    >
      <v-col>
        <v-select
          prepend-icon="filter_alt"
          multiple
          chips
          :items="filters"
        >
        </v-select>
      </v-col>
    </v-row>
    <v-row
      class="subrow"
      no-gutters
    >
      <v-col>
        <v-card
          width="100%"
          class="text-center pa-2 my-2"
        >
          {{numTranslated}} / {{totalEntries}} Translated
        </v-card>
        <v-card
          width="100%"
          class="text-center pa-2 my-2"
        >
          {{numValidated}} / {{totalEntries}} Validated
        </v-card>
      </v-col>
    </v-row>
    <v-row
      class="subrow ml-3"
      no-gutters
    >
      <v-col >
        <v-btn
          dark
        >
          Clear
        </v-btn>
      </v-col>
      <v-col 
        align="center"
      >
        <v-btn
          dark
          @click="$emit('onSubmit')"
        >
          Sumbit
        </v-btn>
      </v-col>
      <v-col 
        align="center"
      >
        <v-btn
          dark
          @click="$emit('goToTop')"
        >
          <v-icon>keyboard_arrow_up</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
export default {
  name: "ToolBox",
  props: {
    numTranslated: { type: Number, required: true },
    numValidated: { type: Number, required: true },
    totalEntries: { type: Number, required: true },
  },
  data() {
    return {
      filters: [
        'Yes',
        'No',
        'Maybe',
        'So',
      ],
    };
  },
  methods: {

  },
};
</script>

<style scoped>
  .subrow {
    height: 25%;
    align-content: center;
  }
</style>