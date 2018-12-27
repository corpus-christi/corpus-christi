<template>
  <div>
    <h4 class="display-1">Locales</h4>

    <p>FOO {{ $t("message.foo") }}</p>

    <ol>
      <li v-for="country in countries" v-bind:key="country.code">
        {{ flag_unicode(country.code) }} {{ country.name }}
      </li>
    </ol>
  </div>
</template>

<script>
import { flagForCountry } from "../helpers";

export default {
  name: "Locale",
  data: function() {
    return {
      countries: [],
      languages: []
    };
  },
  methods: {
    flag_unicode: country_code => flagForCountry(country_code)
  },
  mounted: function() {
    this.$http
      .get("/api/v1/places/countries", {
        params: {
          locale: "en-US"
        }
      })
      .then(response => {
        this.countries = response.data;
      });

    this.$http
      .get("/api/v1/i18n/languages", {
        params: {
          locale: "en-US"
        }
      })
      .then(response => {
        this.languages = response.data;
      });
  }
};
</script>
