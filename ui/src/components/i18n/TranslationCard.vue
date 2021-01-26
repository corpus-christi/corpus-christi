<template>
  <v-card
    v-if="isSelected && !isHiddenByFilters"
    outlined
    class="d-flex align-center ma-3"
    elevation="2"
  >
    <v-card
      width="19.7%"
      elevation="0"
      class="ml-1"
    >
      <v-card-text>
        {{ restOfTag }}
      </v-card-text>
    </v-card>

    <v-card
      width="20.5%"
      elevation="0"
      outlined
    >
      <v-card-text>
        {{ previewGloss }}
      </v-card-text>
    </v-card>

    <v-card
      width="2%"
      elevation="0"
    >
      <v-icon>
        keyboard_arrow_right
      </v-icon>
    </v-card>

    <v-card
      width="20.5%"
      elevation="0"
      outlined
      :class="{ selected : highlightCard }"
    >
      <v-card-text>
        {{ currentGloss }}
      </v-card-text>
    </v-card>

    <!-- SPACER -->
    <v-card min-width=7% />

    <v-card
      width="20%"
      elevation="0"
    >
      <v-card
        width="80%"
        elevation="0"
      >
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
      </v-card>
    </v-card>

    <!-- SPACER -->
    <v-card width="3.7%" />

    <v-card
      width="1%"
      elevation="0"
    >
      <v-checkbox
        class=" align-self-center"
        v-model="newVerification"
        :color="oldVerification ? 'primary' : 'warning'"
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
