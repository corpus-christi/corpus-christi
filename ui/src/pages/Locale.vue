<template>
    <div>
        <h4 class="display-1">Locales</h4>

        <SelectLocale v-bind:locales="locales"></SelectLocale>

        <v-data-table
                v-bind:headers="headers"
                v-bind:items="locales">
            <template slot="items" slot-scope="props">
                <td>{{ props.item.id }}</td>
                <td>{{ props.item.desc }}</td>
            </template>
        </v-data-table>
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
                headers: [
                    {text: "ID", value: "id"},
                    {text: "Description", value: "desc"},
                ],
                locales: []
            };
        },
        mounted: function () {
            axios.get("/api/v1/i18n/locales").then(response => {
                this.locales = response.data.map(locale => ({
                    id: locale.id,
                    country: locale.country,
                    desc: locale.desc
                }));
            });
        }
    };
</script>
