import VueGoogleMaps from "@fawmi/vue-google-maps";
import type { App } from "vue";

const GOOGLE_MAPS_API_KEY = "AIzaSyB9IPbx6gxLz5xW46EDnddSwwAu1FI74MI";

export default {
  install(app: App) {
    app.use(VueGoogleMaps, {
      load: {
        key: GOOGLE_MAPS_API_KEY,
        libraries: "places"
      }
    });
  }
};

export { GOOGLE_MAPS_API_KEY };
