import axios from "axios";
import type { App } from "vue";

const authAxios = axios.create({
  baseURL: "/"
});

authAxios.interceptors.response.use(
  resp => {
    return Promise.resolve(resp);
  },
  error => {
    if (error.response?.status === 401) {
      console.log(error.config);
      // Lazy import to avoid circular dependency with store
      import("../stores/auth").then(({ useAuthStore }) => {
        const authStore = useAuthStore();
        authStore.logOut();
      });
      window.location.replace(
        "login?redirect=" + window.location.toString().replace(/^\/*$/, "")
      );
      return Promise.reject(error);
    } else {
      return Promise.reject(error);
    }
  }
);

export function setJWT(jwt: string | null) {
  if (jwt) {
    authAxios.defaults.headers.common["Authorization"] = `Bearer ${jwt}`;
  } else {
    delete authAxios.defaults.headers.common["Authorization"];
  }
}

const plainAxios = axios.create({
  baseURL: "/"
});

export { authAxios, plainAxios };

export default {
  install(app: App) {
    app.provide("$http", authAxios);
    app.provide("$httpNoAuth", plainAxios);
  }
};
