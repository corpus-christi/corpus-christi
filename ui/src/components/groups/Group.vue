<template>
  <div>
    <v-btn
      outline
      color="primary"
      v-on:click="$router.push({ path: '/groups/all' })"
      ><v-icon>arrow_back</v-icon>{{ $t("actions.back") }}</v-btn
    >
    <v-tabs color="transparent" slider-color="accent">
      <v-tab ripple :to="{ name: 'group-details' }">
        <v-icon left>list</v-icon>{{ $t("groups.details.title") }}
      </v-tab>
      <v-tab ripple :to="{ name: 'group-meetings' }">
        <v-icon left>devices_other</v-icon>{{ $t("groups.meetings.title") }}
      </v-tab>
      <v-tab ripple :to="{ name: 'group-members' }">
        <v-icon left>person</v-icon>{{ $t("groups.members.title") }}
      </v-tab>
      <v-tab ripple :to="{ name: 'group-managers' }">
        <v-icon left>account_circle</v-icon>{{ $t("groups.details.manager") }}
      </v-tab>
    </v-tabs>
    <hr class="vertical-spacer" />
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: "Group",
  data() {
    return {
      tabs: {
        members: 0,
        meetings: 1,
        details: 2
      }
    };
  }
};
</script>

<style scoped>
.vertical-spacer {
  margin-bottom: 16px;
}
</style>
