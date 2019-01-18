<template>
  <div>
    <v-btn
      outline
      color="primary"
      :to="{ path: '/events/all' }"
      ><v-icon>arrow_back</v-icon>Back</v-btn
    >
    <v-tabs color="transparent" slider-color="accent">
      <v-tab
        ripple
        v-on:click="
          $router.push({ path: '/events/' + $route.params.event + '/details' })
        "
      >
        <v-icon>list</v-icon>&nbsp;{{ $t("events.details.title") }}
      </v-tab>
      <v-tab
        ripple
        :to="{
            path: '/events/' + $route.params.event + '/participants'
          }"
      >
        <v-icon>person </v-icon>&nbsp;{{ $t("events.participants.title") }}
      </v-tab>
      <v-tab
        ripple
        :to="{ path: '/events/' + $route.params.event + '/assets' }"
      >
        <v-icon>devices_other</v-icon>&nbsp;{{ $t("assets.title") }}
      </v-tab>
    </v-tabs>
    <hr class="vertical-spacer" />
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: "Event",
  data() {
    return {
      activeTab: null,
      currentPath: this.$route.path,
      currentComponent: "details",
      tabs: {
        details: 0,
        participants: 1,
        assets: 2
      }
    };
  },

};
</script>

<style scoped>
.vertical-spacer {
  margin-bottom: 16px;
}
</style>
