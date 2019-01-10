<template>
    <div>
        <v-tabs color="white" slider-color="accent">
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/details'})">
                <v-icon>list</v-icon>&nbsp;Details
            </v-tab>
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/participants'})">
                <v-icon>person </v-icon>&nbsp;Participants
            </v-tab>
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/teams'})">
                <v-icon>group</v-icon>&nbsp;Teams
            </v-tab>
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/assets'})">
                <v-icon>devices_other</v-icon>&nbsp;Assets
            </v-tab>
        </v-tabs>
        <hr/>
        <router-view></router-view>
    </div>
</template>

<script>
export default {
    name: "Event"
}
</script>
