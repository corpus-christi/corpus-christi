<template>
  <v-app>
    <app-bar />
    <v-main>
      <message-snack-bar v-bind:bus="bus" />
      <error-report-dialog v-bind:bus="bus" />
      <router-view />
    </v-main>
    <Footer />
  </v-app>
</template>

<script>
import AppBar from "./AppBar";
import MessageSnackBar from "../components/MessageSnackBar";
import ErrorReportDialog from "../components/report/ErrorReportDialog";
import Footer from "./Footer";

export default {
  name: "DefaultLayout",
  components: { Footer, AppBar, MessageSnackBar, ErrorReportDialog },
  props: ["bus"],
};
</script>
