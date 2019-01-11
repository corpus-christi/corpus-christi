<template>
    <div>
        <v-btn outline color="primary" v-on:click="$router.push({path: '/events/all'})"><v-icon>arrow_back</v-icon>Back</v-btn>
        <v-tabs color="transparent" slider-color="accent">
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/details'})">
                <v-icon>list</v-icon>&nbsp;{{ $t('events.details.title') }}
            </v-tab>
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/participants'})">
                <v-icon>person </v-icon>&nbsp;{{ $t('events.participants.title') }}
            </v-tab>
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/teams'})">
                <v-icon>group</v-icon>&nbsp;{{ $t('events.teams.title') }}
            </v-tab>
            <v-tab ripple v-on:click="$router.push({path: '/events/' + $route.params.event + '/assets'})">
                <v-icon>devices_other</v-icon>&nbsp;{{ $t('events.assets.title') }}
            </v-tab>
        </v-tabs>
        <hr class="vertical-spacer"/>
        <router-view></router-view>
    </div>
</template>

<script>
export default {
    name: "Event",
    data() {
        return {
            currentPath: this.$route.path,
            currentComponent: 'details'
        }
    },
    watch: {
        
        $route: function(to, from){
            var splitPath = to.fullPath.split('/')
            this.currentComponent = to.fullPath.split('/')[splitPath.length-1]
        }
    }
}
</script>

<style scoped>
.vertical-spacer {
    margin-bottom: 16px
}
</style>
