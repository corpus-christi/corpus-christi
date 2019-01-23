<template>
  <div>
    <v-btn
      outline
      color="primary"
      v-on:click="$router.push({ path: '/groups/all' })"
      ><v-icon>arrow_back</v-icon>Back</v-btn
    >
    <v-tabs color="transparent" slider-color="accent">
      <v-tab
        ripple
        :to="{ path: '/groups/' + $route.params.group + '/details' }"
      >
        <v-icon>list</v-icon>&nbsp;{{ $t("groups.details.title") }}
      </v-tab>
      <v-tab
        ripple
        :to="{ path: '/groups/' + $route.params.group + '/members' }"
      >
        <v-icon>person </v-icon>&nbsp;{{ $t("groups.members.title") }}
      </v-tab>
      <!-- <v-tab
        ripple
        :to="{ path: '/groups/' + $route.params.group + '/meetings' }"
      >
        <v-icon>devices_other</v-icon>&nbsp;{{ $t("groups.meetings.title") }}
      </v-tab> -->
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
        details: 0,
        members: 1,
        meetings: 2
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
