import Vue from "vue";
import axios from "axios";

Vue.prototype.$http = axios;

export function setJWT(jwt) {
  const access_token = `Bearer ${jwt}`;
  axios.defaults.headers.common["Authorization"] = access_token;
}
