<template>
  <v-app>
    <nav-drawer v-model="drawerVisible" />
    <app-bar @toggleDrawer="toggleNavDrawer" />
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
import NavDrawer from "./NavDrawer";
import MessageSnackBar from "../components/MessageSnackBar";
import ErrorReportDialog from "../components/report/ErrorReportDialog";
import Footer from "./Footer";

export default {
  name: "DefaultLayout",
  components: { Footer, AppBar, NavDrawer, MessageSnackBar, ErrorReportDialog },

  data() {
    return {
      drawerVisible: false,
    };
  },

  methods: {
    toggleNavDrawer() {
      this.drawerVisible = !this.drawerVisible;
    },
  },
};
</script>
