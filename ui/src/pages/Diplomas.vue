<template>
  <v-container>
    <!--
    <v-tabs v-model="tab" color="primary" slider-color="accent">
      <v-tab ripple data-cy="person-table-tab">
        <v-icon>person</v-icon>
        &nbsp;{{ $t("people.title") }}
      </v-tab>
      <v-tab ripple data-cy="roles-table-tab">
        <v-icon>supervisor_account</v-icon>
        &nbsp;{{ $t("people.title-roles") }}
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item>
        <router-view></router-view>
      </v-tab-item>
      <v-tab-item>
      </v-tab-item>
    </v-tabs-items> 
    -->
    <router-view></router-view>
  </v-container>
</template>

<script>
export default {
  name: "Diplomas",
  /*
  data() {
    return {
      tab: null,
    };
  },//*/
};
</script>

<style scoped></style>
