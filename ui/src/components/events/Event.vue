<template>
    <div>
        <v-tabs color="transparent" slider-color="accent">
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/details'})">
                <v-icon>list</v-icon>&nbsp;{{ $t('events.details') }}
            </v-tab>
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/participants'})">
                <v-icon>person </v-icon>&nbsp;{{ $t('events.participants') }}
            </v-tab>
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/teams'})">
                <v-icon>group</v-icon>&nbsp;{{ $t('events.teams') }}
            </v-tab>
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/assets'})">
                <v-icon>devices_other</v-icon>&nbsp;{{ $t('events.assets') }}
            </v-tab>
        </v-tabs>
        <hr class="vertical-spacer"/>
        <router-view></router-view>
    </div>
</template>

<script>
export default {
    name: "Event"
}
</script>

<style scoped>
.vertical-spacer {
    margin-bottom: 16px
}
</style>
