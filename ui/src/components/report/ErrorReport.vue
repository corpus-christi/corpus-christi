<template>
  <v-container>
    <v-form>
      <v-textarea
        outlined
        counter
        prepend-icon="announcement"
        v-bind:label="$t('error-report.display.make-description')"
        v-model="userFeedback"
      >
      </v-textarea>
    </v-form>
    <v-btn color="info" @click="submitFeedback()">{{
      $t("error-report.actions.submit")
    }}</v-btn>
    <v-btn color="primary" @click="$emit('error-report-cancel')">{{
      $t("error-report.actions.cancel")
    }}</v-btn>
  </v-container>
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
