<template>
  <v-container>
    <h1>{{ $t("home.title") }}</h1>
    <Login />
  </v-container>
</template>

<script>
import Login from "../components/Login";
export default {
  name: "Home",
  components: { Login }
};
</script>
