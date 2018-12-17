<template>
    <v-flex xs12 sm6 d-flex>
        <v-select
                label="Locales"
                v-bind:items="localesWithFlags" item-value="id" item-text="desc"
                v-bind:value="currentLocale" v-on:input="setCurrentLocale"></v-select>
    </v-flex>
</template>

<script>
    import {mapMutations, mapState} from 'vuex';

    export default {
        name: "SelectLocale",
        props: ['locales'],
        computed: {
            localesWithFlags: function () {
                return this.locales.map(locale => ({
                    id: locale.id,
                    desc: this.flag(locale.country) + ' ' + locale.desc
                }));
            },
            ...mapState(['currentLocale'])
        },
        methods: {
            // Convert a two-letter country code into the Unicode characters for its flag.
            flag(country) {
                const regionalIndicatorA = 0x1F1e6;
                country = country.toUpperCase();
                if (/^[A-Z]{2}$/.test(country)) {
                    let vals = country.split('').map(ch => ch.charCodeAt(0) - 'A'.charCodeAt(0) + regionalIndicatorA);
                    return String.fromCodePoint.apply(null, vals);
                } else {
                    return 'XX';
                }
            },
            ...mapMutations(['setCurrentLocale'])
        }
    }
</script>
