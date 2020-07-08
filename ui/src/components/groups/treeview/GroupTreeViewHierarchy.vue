<template>
  <div>
    <v-treeview
      v-if="!$data.$_groupHierarchyMixin_loading"
      :items="$_groupHierarchyMixin_adminTree"
    ></v-treeview>
  </div>
</template>
<script>
import groupHierarchyMixin from "../../../mixins/groupHierarchyMixin.js";
export default {
  mixins: [groupHierarchyMixin],
  data() {
    return {};
  },
  computed: {},
  mounted() {
    console.log("treeview component mounted");
  }
};
</script>
