<template>
  <v-app>
    <!-- Places the App Bar -->
    <app-bar />
    <v-main>
      <message-snack-bar v-bind:bus="bus" />
      <error-report-dialog v-bind:bus="bus" />
      <router-view />
    </v-main>

    <!-- Places the Footer -->
    <Footer />
  </v-app>
</template>

<script>
/**
 * @file
 * @name DefaultLayout.vue
 */
import AppBar from "./AppBar";
import MessageSnackBar from "../components/MessageSnackBar";
import ErrorReportDialog from "../components/report/ErrorReportDialog";
import Footer from "./Footer";

/**
 * @module
 * @name DefaultLayout
 * @exports ../App.vue
 * Configures the basic layout of all pages.
 */
export default {
  name: "DefaultLayout",
  components: { Footer, AppBar, MessageSnackBar, ErrorReportDialog },
  props: ["bus"],
};
</script>
