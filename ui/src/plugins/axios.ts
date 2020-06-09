import Vue from "vue";
import axios from "axios";
import store from "../store.js";
import { eventBus } from "../plugins/event-bus.js";
import { getResponseErrorKey } from "../plugins/vue-i18n.js";

const authAxios = axios.create({
  baseURL: "/"
  // headers: { "Authorization": "Bearer NOT SET" }
});

authAxios.interceptors.response.use(
  resp => {
    return Promise.resolve(resp);
  },
  error => {
    if (error.response.status >= 400) {
      /* display a snack bar with error, while enabling the user to submit a error report */
      // TODO: Currently all failure reponses with 400+ status code will be displayed to the user.
      // Is this too much? Should we put this error interceptor somewhere else to catch only those unhandled?
      // <2020-06-08, David Deng> //
      eventBus.$emit("error", {
        content: getResponseErrorKey(error.response.status),
        action: {
          title: "error-report.actions.report-error",
          func: (vm: Vue) =>
            eventBus.$emit("show-error-report-dialog", {
              props: {
                time_stamp: new Date().toISOString(),
                status_code: error.response.status,
                endpoint: error.response.config.url
              }
            })
        }
      });
      console.log(error.response);
    }
    if (error.response.status === 401) {
      console.log(error.config);
      store.commit("logOut");
      window.location.replace(
        "login?redirect=" + window.location.toString().replace(/^\/*$/, "")
      );
    }
    return Promise.reject(error);
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
