/**
 * @file
 * @name axios.js
 * @exports ???
 * @todo Add comments describing what this file does and where it's imported to.
 */
import Vue from "vue";
import axios from "axios";
import store from "../store.js";
import router from "../router.js";
import { eventBus } from "@/plugins/event-bus";
import { getResponseErrorKey } from "@/plugins/vue-i18n";

const authAxios = axios.create({
  baseURL: "/",
  // headers: { "Authorization": "Bearer NOT SET" }
});

authAxios.interceptors.response.use(
  (resp) => {
    return Promise.resolve(resp);
  },
  (error) => {
    if (error.response.status >= 400) {
      /* display a snack bar with error, while enabling the user to submit a error report */
      /* to disable, include a 'noErrorSnackBar' in the request config. e.g.
       *    authAxios
       *    .post('some/url', payload, { noErrorSnackBar: true })
       *    .then(handleSuccess)
       *    .catch(handleErrorMyself)
       */
      if (!error.response.config.noErrorSnackBar) {
        eventBus.$emit("error", {
          content: getResponseErrorKey(error.response.status),
          action: {
            title: "error-report.actions.report-error",
            func: () =>
              eventBus.$emit("show-error-report-dialog", {
                props: {
                  time_stamp: new Date().toISOString(),
                  status_code: error.response.status,
                  endpoint: error.response.config.url,
                },
              }),
          },
        });
      }
      console.log(error.response);
    }
    if (error.response.status === 401) {
      console.log(error.config);
      router.replace({
        name: "login",
        query: { redirect: router.currentRoute.name },
      });
      store.commit("logOut");
    }
    return Promise.reject(error);
  }
);

Vue.prototype.$http = authAxios;

export function setJWT(jwt) {
  authAxios.defaults.headers.common["Authorization"] = `Bearer ${jwt}`;
}

const plainAxios = axios.create({
  baseURL: "/",
});

Vue.prototype.$httpNoAuth = plainAxios;
