<template>
  <v-dialog
    v-model="showSelf"
    max-width="550px"
  >
    <v-card>
      <v-card-title class="justify-center">
        Enter locale code and description
      </v-card-title>
      <v-card-subtitle> <!-- Try to make this centered -->
        (Ex: en-US English US)
      </v-card-subtitle>
      <v-col class="d-flex justify-space-between">
        <v-text-field v-model="languageCode"
          outlined label="Language Code" hint="(Ex: en)"
        />
        <v-icon class="mb-7">
          horizontal_rule
        </v-icon>
        <v-text-field v-model="countryCode"
          outlined label="Country ISO Code" hint="(Ex: US)"
        />
        <v-text-field v-model="description"
          class="ml-5" outlined label="Description" hint="(Ex: English US)"
        />
      </v-col>
      <v-card-actions class="d-flex justify-space-between">
        <v-btn color="error lighten-2" @click="$emit('closeDialog')" outlined>
          Cancel
        </v-btn>
        <v-btn
          :loading="submissionInProgress"
          color="primary" @click="submitButtonClicked" outlined
        >
          Sumbit
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: "NewLocaleDialog",
  props: {
    showDialog: { type: Boolean, required: true },
  },
  data() {
    return{
      languageCode: "",
      countryCode: "",
      description: "",

      submissionInProgress: false,
      errorMessage: "",
      showSelf: false,
    };
  },
  watch: {
    showDialog: function() {
      this.showSelf = this.showDialog;
    },
    showSelf: function() {
      if (!this.showSelf) {
        this.$emit('closeDialog');
      }
    },
  },
  computed: {
    localeCode() {
      return `${this.languageCode}-${this.countryCode}`;
    }
  },
  methods: {
    submitButtonClicked() {
      let newLocaleObject = { code: this.localeCode, desc: this.description };
      this.submissionInProgress = true;
      this.$http
        .post('api/v1/i18n/locales', newLocaleObject)
        .then(() => {
          this.$emit('submitComplete', newLocaleObject);
        })
        .catch((err) => {
          console.log(err);
        })
        .finally(() => {
          this.submissionInProgress = false;
        })
    },
  },
};
</script>
