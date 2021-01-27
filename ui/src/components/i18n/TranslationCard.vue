<template>
  <v-card v-if="isSelected && !isHiddenByFilters" class="mb-1" outlined>
    <v-container>
      <v-row align="center">
        <v-col>
          {{ restOfTag }}
        </v-col>

        <v-col>
          {{ previewGloss }}
        </v-col>

        <v-col cols="1">
        <v-icon>keyboard_arrow_right</v-icon>
        </v-col>

        <v-col>
          {{ currentGloss }}
        </v-col>

        <v-col cols="3">
          <v-text-field
            v-model="newTranslation"
            :append-icon="newTranslation ? 'send' : ''"
            :loading="submissionInProgress ? 'success' : false"
            @click:append="submitChange"
            @focus="toggleSelection"
            @blur="toggleSelection"
          >
            {{ newTranslation }}
          </v-text-field>
        </v-col>

        <v-col cols="1">
          <v-checkbox
            class="align-self-center"
            v-model="newVerification"
            :color="oldVerification ? 'primary' : 'warning'"
          />
        </v-col>
      </v-row>
    </v-container>
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
    filters:         { type: Array,   required: true },
    selectedTags:    { type: Array,   required: true },
    currentCode:     { type: String,  required: true },
  },
  data() {
    return{
      oldTranslation: this.currentGloss,
      newTranslation: "",
      oldVerification: this.currentVerified,
      newVerification: this.currentVerified,
      submissionInProgress: false,
      highlightCard: false,
    };
  },
  watch: {
    currentGloss: function() {
      this.newTranslation = "";
      this.oldVerification = this.currentVerified;
      this.newVerification = this.currentVerified;
    },
  },
  computed: {
    isSelected() {
      return this.selectedTags.includes(this.topLevelTag);
    },
    changedKey() {
      return `${this.topLevelTag}.${this.restOfTag}`;
    },
    isHiddenByFilters() {
      if (this.currentVerified && this.filters.includes('Unverified')) {
        return true;
      }
      if (this.currentGloss.length != 0 && this.filters.includes('Untranslated')) {
        return true;
      }
      return false;
    },
  },
  methods: {
    submitChange() {
      this.submissionInProgress = true;
      this.$http
        .patch(`api/v1/i18n/values/update`, {
          key_id: `${this.topLevelTag}.${this.restOfTag}`,
          locale_code: this.currentCode,
          gloss: this.newTranslation,
          verified: this.newVerification,
        })
        .then(() => {
          this.$emit('submitAChange', this.myIndex, this.newTranslation, this.newVerification);
          this.oldTranslation = this.newTranslation;
          this.newTranslation = "";
          this.oldVerification = this.newVerification;
        })
        .catch((err) => {
          console.log(err);
        })
        .finally(() => {
          this.submissionInProgress = false;
        });
    },
    toggleSelection() {
      this.highlightCard = !this.highlightCard;
    },
  },
};
</script>

<style scoped>
  .selected{
    border-color: #1874d2;
  }
</style>