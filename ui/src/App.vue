<template>
    <v-app>
        <v-toolbar app>
            <v-toolbar-title class="headline text-uppercase">
                <span>Corpus</span>
                <span class="font-weight-light">Christi</span>
            </v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn flat v-bind:to="{ name: 'locale' }">Locale</v-btn>
            <v-btn flat v-bind:to="{ name: 'home' }">Home</v-btn>
        </v-toolbar>

        <v-content>
            <v-container>
                <router-view></router-view>
            </v-container>
        </v-content>
    </v-app>
</template>

<script>
    export default {
        name: 'App'
    }
</script>
