<template>
    <div>
        <h4 class="display-1">Locales</h4>

        <SelectLocale v-bind:locales="locales"></SelectLocale>

        <p>FOO {{ $t("message.foo") }}</p>

        <ol>
            <li v-for="country in countries">
                {{ flag(country.code )}}
                {{ country.name }}
            </li>
        </ol>

    </div>
</template>

<script>
    import SelectLocale from "../components/SelectLocale";

    const axios = require("axios");

    export default {
        name: "Locale",
        components: {SelectLocale},
        data: function () {
            return {
                locales: [],
                countries: [],
                languages: []
            };
        },
        methods: {
            flag(country) {
                const regionalIndicatorA = 0x1F1e6;
                country = country.toUpperCase();
                if (/^[A-Z]{2}$/.test(country)) {
                    let vals = country.split('').map(ch => ch.charCodeAt(0) - 'A'.charCodeAt(0) + regionalIndicatorA);
                    return String.fromCodePoint.apply(null, vals);
                } else {
                    return 'XX';
                }
            }
        },
        mounted: function () {
            axios.get("/api/v1/i18n/locales").then(response => {
                this.locales = response.data.map(locale => ({
                    id: locale.id,
                    country: locale.country,
                    desc: locale.desc
                }));
            });

            axios.get("/api/v1/i18n/countries").then(response => {
                this.countries = response.data;
            });

            axios.get("/api/v1/i18n/languages").then(response => {
                this.languages = response.data;
            });
        }
    };
</script>
