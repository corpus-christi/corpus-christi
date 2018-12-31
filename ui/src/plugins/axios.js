import Vue from "vue";
import axios from "axios";

const authAxios = axios.create({
  baseUrl: "/"
  // headers: { "Authorization": "Bearer NOT SET" }
});
Vue.prototype.$http = authAxios;

export function setJWT(jwt) {
  const access_token = `Bearer ${jwt}`;
  authAxios.defaults.headers.common["Authorization"] = access_token;
}

const plainAxios = axios.create({
  baseUrl: "/"
});
Vue.prototype.$httpNoAuth = plainAxios;
