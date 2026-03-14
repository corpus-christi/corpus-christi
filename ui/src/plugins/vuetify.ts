import { createVuetify } from "vuetify";
import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";

export default createVuetify({
  icons: {
    defaultSet: "mdi"
  },
  theme: {
    defaultTheme: "light"
  }
});
