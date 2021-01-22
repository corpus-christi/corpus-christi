<template>
  <v-card
    class="mr-2"
    outlined
    elevation="2"
    v-if="shouldBeShown"
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
          <v-icon>add_circle_outline</v-icon>
          Add New Locale
        </v-btn>
      </v-col>
      <v-col
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
          item-value="id"
          @change="onChange"
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
          {{numValidated}} / {{totalEntries}} Verified
        </v-card>
      </v-col>
    </v-row>
    <v-row
      class="subrow ml-3"
      no-gutters
    >
      <v-col 
        align="center"
      >
        <v-btn
          dark
          @click="$emit('hideToolBox')"
        >
          Hide
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
    shouldBeShown: { type: Boolean, required: true },
  },
  data() {
    return {
      filters: [
        { text: 'Unverified', id: 0 },
        { text: 'Untranslated', id: 1 },
      ],
      filtersObj: {
        Unverified: false,
        Untranslated: false,
      },
    };
  },
  methods: {
    onChange(key) {
      this.resetFiltersObj();
      this.createFiltersObj(key);
      console.log(this.filtersObj);
      this.$emit('sendFilters', this.filtersObj);
    },
    createFiltersObj(key) {
      for (var i = 0; i < key.length; i++) {
        if(key[i] == 0) {
          this.filtersObj.Unverified = true;
        }
        else {
          this.filtersObj.Untranslated = true;
        }
      }
    },
    resetFiltersObj() {
      this.filtersObj.Untranslated = false;
      this.filtersObj.Unverified = false;
    }
  },
  mounted: function() {
    this.$emit('sendFilters', this.filtersObj);
  }
};
</script>

<style scoped>
  .subrow {
    height: 25%;
    align-content: center;
  }
</style>