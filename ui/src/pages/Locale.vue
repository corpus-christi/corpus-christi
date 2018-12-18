<template>
    <div>
        <h4 class="display-1">Locales</h4>

        <SelectLocale v-bind:locales="locales"></SelectLocale>

        <p>FOO {{ $t("message.foo") }}</p>

        <ol>
            <li v-for="country in countries" v-bind:key="country.code">
                {{ flag_unicode(country.code) }}
                {{ country.name }}
            </li>
        </ol>

    </div>
</template>

<script>
    import SelectLocale from "../components/SelectLocale";
    import {flagForCountry} from "../helpers";

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
            flag_unicode: (country_code) => flagForCountry(country_code)
        },
        mounted: function () {
            axios.get("/api/v1/i18n/locales").then(response => {
                this.locales = response.data;
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
