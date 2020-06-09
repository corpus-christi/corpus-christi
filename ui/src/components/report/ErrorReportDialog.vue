<template>
  <!-- display an dialog to report error
    usage: <ErrorReportDialog v-bind:bus="bus"></ErrorReportDialog>
      where bus is a vue instance.
    To display the dialog, do:
      bus.$emit('show-error-report-dialog', config: {
        props: [...]
      })
    where 'props' will be passed in as the ErrorReport component props
  -->
  <v-dialog max-width="600" persistent v-model="show">
    <v-card>
      <ErrorReport
        v-on:error-report-cancel="handleCancel"
        v-on:error-report-success="handleSuccess"
        v-on:error-report-fail="handleFail"
        v-bind="errorReportProps"
      ></ErrorReport>
    </v-card>
  </v-dialog>
</template>
<script>
import ErrorReport from "./ErrorReport.vue";
export default {
  props: ["bus"],
  components: { ErrorReport },
  data() {
    return {
      show: false,
      errorReportProps: []
    };
  },
  mounted() {
    this.bus.$on("show-error-report-dialog", this.handleShow);
  },
  methods: {
    handleShow(config) {
      if (config.props) this.errorReportProps = config.props;
      this.show = true;
    },
    handleCancel() {
      this.show = false;
    },
    handleSuccess() {
      this.show = false;
      this.bus.$emit("message", {
        content: "error-report.display.feedback-successful"
      });
    },
    handleFail(err) {
      console.log("error in ErrorReportDialog");
      console.log(err);
    }
  }
};
</script>
