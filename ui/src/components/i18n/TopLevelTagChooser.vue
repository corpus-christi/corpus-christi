<template>
  <v-card-text>
    <v-list 
      elevation="2"
      rounded
    >
      <v-list-item-group
        color="grey darken-4"
        multiple
      >
        <v-checkbox
          v-for="(tag, index) in topLevelTags"
          :key="index"
          v-model="selectedTags"
          :label="tag"
          :value="tag"
          @click="onTagsChanged"
        />
      </v-list-item-group>
    </v-list>
  </v-card-text>
</template>

<script>
export default {
  name: "TopLevelTagChooser",
  props: {
    topLevelTags: { type: Array, required: true, },
  },

  data() {
    return {
      selectedTags: [],
    };
  },

  computed: {
    isSelected() {
      return this.selectedTags.includes(this.topLevelTag);
    },
  },

  methods: {
    onTagsChanged() {
      this.$emit("tagsUpdated", this.selectedTags);
    },
  },
};
</script>
