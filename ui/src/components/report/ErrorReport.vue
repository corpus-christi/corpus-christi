<template>
  <v-card>
    <v-card-title>
      {{ $t("error-report.title") }}
    </v-card-title>
    <v-card-text>
      <v-form>
        <v-textarea
          outlined
          counter
          v-bind:label="$t('error-report.display.make-description')"
          v-model="userFeedback"
        >
        </v-textarea>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn text @click="$emit('error-report-cancel')">
        {{ $t("error-report.actions.cancel") }}
      </v-btn>
      <v-btn color="primary" @click="submitFeedback()">
        {{ $t("error-report.actions.submit") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: "ErrorReport",
  data() {
    return {
      userFeedback: "",
    };
  },
  props: {
    endpoint: {
      type: String,
      default: null,
    },
    time_stamp: {
      type: String,
      default: null,
    },
    status_code: {
      type: Number,
      default: null,
    },
  },
  methods: {
    submitFeedback() {
      return this.$http
        .post("/api/v1/error-report/", {
          description: this.userFeedback,
          endpoint: this.endpoint,
          time_stamp: this.time_stamp,
          status_code: this.status_code,
        })
        .then(() => {
          this.userFeedback = "";
          this.$emit("error-report-success");
        })
        .catch((err) => {
          this.$emit("error-report-fail", err);
        });
    },
  },
};
</script>
