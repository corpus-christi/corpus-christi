<template>
  <v-card
    v-if="isSelected && isFiltered"
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
        :append-icon="newTranslation ? 'send' : ''"
        :loading="submissionInProgress ? 'success' : false"
        @input="emitEventChanged"
        @click:append="submitChange"
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
    myIndex:         { type: Number,  required: true },
    topLevelTag:     { type: String,  required: true },
    restOfTag:       { type: String,  required: true },
    previewGloss:    { type: String,  required: true },
    currentGloss:    { type: String,  required: true },
    currentVerified: { type: Boolean, required: true },
    filters:         { type: Object,  required: true },
    selectedTags:    { type: Array,   required: true },
    currentCode:     { type: String,  required: true },
  },
  data() {
    return{
      oldTranslation: this.currentGloss,
      newTranslation: "",
      oldValidation: this.currentVerified,
      newValidation: this.currentVerified,
      submissionInProgress: false,
    };
  },
  computed: {
    isSelected() {
      return this.selectedTags.includes(this.topLevelTag);
    },
    changedKey() {
      return `${this.topLevelTag}.${this.restOfTag}`;
    },
    isFiltered() {
      return !(this.currentVerified && this.filters.Unverified) && ((this.currentGloss == "") || !this.filters.Untranslated);
    },
  },
  methods: {
    emitEventChanged() {
      if (this.newTranslation === '') {
        this.$emit('clearFromList', this.changedKey);
      }
      else {
        this.$emit('appendToList', this.changedKey, this.newTranslation, this.oldTranslation);
      }
      this.newValidation = false;
    },
    onValidationClick() {
      this.$emit('validationChanged', this.changedKey, this.newValidation, this.oldValidation);
    },
    submitChange() {
      this.submissionInProgress = true;
      this.$http
        .patch(`api/v1/i18n/values/update`, {
          key_id: `${this.topLevelTag}.${this.restOfTag}`,
          locale_code: this.currentCode,
          gloss: this.newTranslation,
          verified: this.newValidation,
        })
        .then(() => {
          this.$emit('submitAChange', this.myIndex, this.newTranslation, this.newValidation);
          this.oldTranslation = this.newTranslation;
          this.newTranslation = "";
          this.oldValidation = this.newValidation;
        })
        .catch((err) => {
          console.log(err);
        })
        .finally(() => {
          this.submissionInProgress = false;
        });
    },
  }
};
</script>
