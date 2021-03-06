<template>
  <v-dialog v-model="showSelf" max-width="550px">
    <v-card>
      <v-card-title class="justify-center">
        {{ $t("translation.locale.title") }}
      </v-card-title>
      <v-card-subtitle>
        {{ $t("translation.locale.hint") }}
      </v-card-subtitle>
      <v-col class="d-flex justify-space-between">
        <v-text-field
          v-model="languageCode"
          :label="$t('translation.locale.language-code.prompt')"
          :hint="$t('translation.locale.language-code.hint')"
          outlined
        />
        <v-icon class="mb-7">horizontal_rule</v-icon>
        <v-text-field
          v-model="countryCode"
          :label="$t('translation.locale.country-code.prompt')"
          :hint="$t('translation.locale.country-code.hint')"
          outlined
        />
        <v-text-field
          v-model="description"
          class="ml-4"
          :label="$t('translation.locale.description.prompt')"
          :hint="$t('translation.locale.description.hint')"
          outlined
        />
      </v-col>
      <v-card-actions class="d-flex justify-space-between">
        <v-btn color="error lighten-2" @click="$emit('closeDialog')" outlined>
          {{ $t("actions.cancel") }}
        </v-btn>
        <v-btn
          :loading="submissionInProgress"
          @click="submitButtonClicked"
          color="primary"
          outlined
        >
          {{ $t("actions.submit") }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { eventBus } from "../../plugins/event-bus";
export default {
  name: "NewLocaleDialog",
  props: {
    showDialog: { type: Boolean, required: true },
  },
  data() {
    return {
      languageCode: "",
      countryCode: "",
      description: "",

      submissionInProgress: false,
      errorMessage: "",
      showSelf: false,
    };
  },
  watch: {
    showDialog: function () {
      this.showSelf = this.showDialog;
    },
    showSelf: function () {
      if (!this.showSelf) {
        //Ensure 'Translation.newLocaleDialog' syncs
        this.$emit("closeDialog");
      }
    },
  },
  computed: {
    localeCode() {
      return `${this.languageCode}-${this.countryCode}`;
    },
  },
  methods: {
    submitButtonClicked() {
      let newLocaleObject = { code: this.localeCode, desc: this.description };
      this.submissionInProgress = true;
      this.$http
        .post("api/v1/i18n/locales", newLocaleObject)
        .then(() => {
          this.$emit("submitComplete", newLocaleObject);
        })
        .catch((err) => {
          eventBus.$emit("error", { content: err });
        })
        .finally(() => {
          this.submissionInProgress = false;
        });
    },
  },
};
</script>
