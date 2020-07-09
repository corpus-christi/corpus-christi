<template>
  <nav>
    <arco-app-bar v-if="$route.meta.layout === 'arco'" />
    <standard-app-bar v-else />
  </nav>
</template>

<script>
import StandardAppBar from "./app-bars/StandardAppBar";
import ArcoAppBar from "./app-bars/ArcoAppBar";

export default {
  name: "AppBar",
  components: { StandardAppBar, ArcoAppBar },
};
</script>
