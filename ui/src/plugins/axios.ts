import Vue from "vue";
import axios from "axios";
import VueAxios from "vue-axios";
import store from "../store.js";

Vue.use(VueAxios, axios);

const authAxios = axios.create({
  baseURL: "/"
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
        "login?redirect=" + window.location.toString().replace(/^\/*$/, "")
      );
      return Promise.reject(error);
    } else {
      return Promise.reject(error);
    }
  }
);

Vue.prototype.$http = authAxios;

export function setJWT(jwt: string) {
  authAxios.defaults.headers.common["Authorization"] = `Bearer ${jwt}`;
}

const plainAxios = axios.create({
  baseURL: "/"
});

Vue.prototype.$httpNoAuth = plainAxios;
