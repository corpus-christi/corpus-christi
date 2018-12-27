import Vue from "vue";
import axios from "axios";

import store from "../store";

axios.defaults.headers.common["Authorization"] = `Bearer ${
  store.getters.currentJWT
}`;

Vue.prototype.$http = axios;
