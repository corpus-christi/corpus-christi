<template>
    <v-flex xs12 sm6 d-flex>
        <v-select
                label="Locales"
                v-bind:items="locales" item-value="id" item-text="desc"
                v-bind:value="currentLocale" v-on:input="setCurrentLocale"
        ></v-select>
    </v-flex>
</template>

<script>
    import {mapMutations, mapState} from 'vuex';

    export default {
        name: "SelectLocale",
        props: ['locales'],
        computed: mapState(['currentLocale']),
        methods: mapMutations(['setCurrentLocale'])
    }
</script>
