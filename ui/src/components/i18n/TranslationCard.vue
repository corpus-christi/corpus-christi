<template>
  <v-card
    v-if="isSelected"
    outlined
    class="d-flex align-center ml-3 mt-4 mr-3"
    elevation="2"
  >
    <v-card
      min-width=19.7%
      max-width=19.7%
      elevation="0"
      class="ml-1"
    >
      <v-card-text>
        {{ restOfTag }}
      </v-card-text>
    </v-card>

    <v-card
      min-width=20.5%
      max-width=20.5%
      elevation="0"
      outlined
    >
      <v-card-text>
        {{ previewGloss }}
      </v-card-text>
    </v-card>

    <v-card
      min-width=1%
      elevation="0"
    >
      <v-icon>
        keyboard_arrow_right
      </v-icon>
    </v-card>

    <v-card
      min-width=20.5%
      max-width=20.5%
      elevation="0"
      outlined
    >
      <v-card-text>
        {{ currentGloss }}
      </v-card-text>
    </v-card>

    <!-- SPACER -->
    <v-card min-width=7% />

    <v-card
      min-width=20%
      max-width=20%
      elevation="0"
    >
      <v-card
        min-width=80%
        max-width=80%
        elevation="0"
      >
        <v-text-field
        v-model="newTranslation"
        @input="emitEventChanged"
        >
          {{ newTranslation }}
        </v-text-field>
      </v-card>
    </v-card>

    <!-- SPACER -->
    <v-card min-width=3.7% />

    <v-card
      min-width=1%
      max-width=1%
      elevation="0"
    >
      <v-checkbox
        class=" align-self-center"
        v-model="newValidation"
        @click="onValidationClick"
      />
    </v-card>
  </v-card>
</template>

<script>
export default {
  name: "TranslationCard",
  props: {
    topLevelTag:     { type: String,  required: true },
    restOfTag:       { type: String,  required: true },
    previewGloss:    { type: String,  required: true },
    currentGloss:    { type: String,  required: true },
    currentVerified: { type: Boolean, required: true },
    selectedTags:    { type: Array,   required: true },
  },
  data() {
    return{
      oldTranslation: this.currentGloss,
      newTranslation: "",

      oldValidation: this.currentVerified,
      newValidation: this.currentVerified, //copy
    };
  },
  computed: {
    isSelected() {
      return this.selectedTags.includes(this.topLevelTag);
    },
    changedKey() {
      return `${this.topLevelTag}.${this.restOfTag}`;
    }
  },
  methods: {
    emitEventChanged() {
      this.$emit('AppendToList', this.changedKey, this.newTranslation, this.oldTranslation);
    },
    onValidationClick() {
      this.$emit('ValidationChanged', this.changedKey, this.newValidation, this.oldValidation);
    },
  }
};
</script>
