/**
 * @file
 * @name google-maps.js
 * Operates the Google Maps plugin from the main Public page.
 * @todo Add comments describing where this file's imported to.
 */
import Vue from "vue";
import * as VueGoogleMaps from "vue2-google-maps";
import Geocoder from "@pderas/vue2-geocoder";

// Store your Google Maps API key in a top-level `.env` file
// with the indicated key (`VUE_APP_...`). Vue CLI will read
// it and replace it here.
const GOOGLE_MAPS_API_KEY = process.env.VUE_APP_GOOGLE_MAPS_API_KEY;

Vue.use(VueGoogleMaps, {
  load: {
    key: GOOGLE_MAPS_API_KEY,
    libraries: "places",
  },
});

Vue.use(Geocoder, {
  googleMapsApiKey: GOOGLE_MAPS_API_KEY,
});
