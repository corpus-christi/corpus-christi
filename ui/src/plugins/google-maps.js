import Vue from "vue";
import * as VueGoogleMaps from "vue2-google-maps";

Vue.use(VueGoogleMaps, {
  load: {
    key: "AIzaSyB9IPbx6gxLz5xW46EDnddSwwAu1FI74MI",
    libraries: "places"
  }
});
