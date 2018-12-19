<template>
    <v-toolbar app>
        <v-toolbar-title class="headline text-uppercase">
            <span>Corpus</span>
            <span class="font-weight-light">Christi</span>
        </v-toolbar-title>
        <v-spacer></v-spacer>

        <v-menu>
            <v-btn flat slot="activator">{{ currentLocaleCode }}</v-btn>
            <v-list>
                <v-list-tile v-for="locale in locales"
                             v-bind:key="locale.id"
                             v-on:click="setCurrentLocale(locale.id)">
                    <v-list-tile-title>{{ locale.desc }}</v-list-tile-title>
                </v-list-tile>
            </v-list>
        </v-menu>

        <v-btn flat v-bind:to="{ name: 'home' }">Home</v-btn>
    </v-toolbar>
</template>

<script>
    import {mapMutations, mapState} from 'vuex';

    export default {
        name: "Toolbar",
        computed: {
            ...mapState(['currentLocaleCode', 'locales']),
        },
        methods: mapMutations(['setCurrentLocale'])
    }
</script>
