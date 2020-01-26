import { AxiosStatic } from "axios";
declare module "vue/types/vue" {
  interface Vue {
    $http: AxiosStatic;
  }
}
