<template>
    <v-flex xs12 sm6 d-flex>
        <v-select data-cy="locale-select"
                  label="Locales"
                  v-bind:items="localesWithFlags" item-value="id" item-text="desc"
                  v-bind:value="currentLocale" v-on:input="setCurrentLocale"></v-select>
    </v-flex>
</template>

<script>
    import {mapMutations, mapState} from 'vuex';
    import {flagForLocale} from "../helpers";

    export default {
        name: "SelectLocale",
        props: ['locales'],
        computed: {
            localesWithFlags: function () {
                return this.locales.map(locale => ({
                    id: locale.id,
                    desc: flagForLocale(locale.id) + ' ' + locale.desc
                }));
            },
            ...mapState(['currentLocale'])
        },
        methods: {
            ...mapMutations(['setCurrentLocale'])
        }
    }
</script>
