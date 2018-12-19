<template>
    <v-app>
        <Toolbar></Toolbar>
        <v-content>
            <v-container>
                <router-view></router-view>
            </v-container>
        </v-content>
    </v-app>
</template>

<script>
    import Toolbar from "./components/Toolbar";
    import {mapActions} from 'vuex';

    export default {
        name: 'App',
        components: {Toolbar},
        methods: mapActions(['initApp']),
        created: function () {
            // Initialize early application stuff (e.g., async requests to server).
            this.initApp();
        }
    }
</script>
