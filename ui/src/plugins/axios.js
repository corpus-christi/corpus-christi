import Vue from "vue";
import axios from "axios";
import store from "../store.js";

const authAxios = axios.create({
  baseUrl: "/"
  // headers: { "Authorization": "Bearer NOT SET" }
});

authAxios.interceptors.response.use(
  resp => {
    return Promise.resolve(resp);
  },
  error => {
    if (error.response.status === 401) {
      console.log(error.config);
      store.commit("logOut");
      window.location.replace(
        window.location,
        "login?redirect=" + window.location.replace(/^\/*$/, "")
      );
      return Promise.reject(error);
    } else {
      return Promise.reject(error);
    }
  }
);

Vue.prototype.$http = authAxios;

export function setJWT(jwt) {
  const access_token = `Bearer ${jwt}`;
  authAxios.defaults.headers.common["Authorization"] = access_token;
}

const plainAxios = axios.create({
  baseUrl: "/"
});
Vue.prototype.$httpNoAuth = plainAxios;
