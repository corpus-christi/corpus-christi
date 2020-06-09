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
    <v-btn color="info" @click="submitFeedback().then(redirect)">{{
      $t("error-report.actions.submit")
    }}</v-btn>
    <v-btn color="primary" @click="redirect">{{
      $t("error-report.actions.cancel")
    }}</v-btn>
  </v-container>
</template>

<script>
import { eventBus } from "../plugins/event-bus.js";
export default {
  name: "ErrorReport",
  data() {
    return {
      userFeedback: ""
    };
  },
  props: {
    endpoint: {
      type: String,
      default: null
    },
    time_stamp: {
      type: String,
      default: new Date().toISOString()
    },
    status_code: {
      type: Number,
      default: null
    }
  },
  methods: {
    submitFeedback() {
      return this.$http
        .post("/api/v1/error-report/", {
          description: this.userFeedback,
          endpoint: this.endpoint,
          time_stamp: this.time_stamp,
          status_code: this.status_code
        })
        .then(() => {
          eventBus.$emit("message", {
            // TODO: currently if the redirected page produces an error, it will override this success message.
            // has to do with displaying multiple messages in the MessageSnackBar component <2020-06-08, David Deng>
            content: "Successfully sent feedback!",
            noTranslate: true
          });
        });
    },
    redirect() {
      let target = this.$route.query.redirect
        ? this.$route.query.redirect
        : { name: "public" };
      this.$router.push(target);
    }
  }
};
</script>
