<template>
  <nav>
    <ArcoToolbar v-if="$route.meta.layout == 'arco'"></ArcoToolbar>
    <StandardToolbar v-else></StandardToolbar>
  </nav>
</template>

<script>
import ArcoToolbar from "./toolbars/Arco";
import StandardToolbar from "./toolbars/Standard";
export default {
  name: "Toolbar",
  components: { StandardToolbar, ArcoToolbar }
};
</script>
