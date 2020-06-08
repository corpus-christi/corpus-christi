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
    <v-btn color="info" @click="submitFeedback().then(redirect)">{{ $t("error-report.actions.submit") }}</v-btn>
    <v-btn color="primary" @click="redirect">{{
      $t("error-report.actions.cancel")
    }}</v-btn>
  </v-container>
</template>

<script>
export default {
  name: "ErrorReport",
  data() {
    return {
      userFeedback: ""
    };
  },
  props: {},
  methods: {
    submitFeedback() {
      return true
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
