import { createLocalVue, shallowMount } from "@vue/test-utils";
import { flagForCountry } from "../../src/helpers";
import Toolbar from "../../src/components/Toolbar";
import Vuetify from "vuetify";
import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuetify);

const localVue = createLocalVue();
localVue.use(Vuex);

describe("CC Toolbar", () => {
  const testLocales = [
    { code: "en-US", desc: "English US" },
    { code: "es-EC", desc: "Español Ecuador" }
  ];
  // TODO: This store basically replicates the real one. That's stupid. Refactor!
  const store = new Vuex.Store({
    state: {
      currentLocaleCode: "en-US",
      locales: testLocales
    },
    getters: {
      currentLocale(state) {
        return state.locales.find(loc => loc.code === state.currentLocaleCode);
      }
    },
    mutations: {
      setCurrentLocaleCode(state, code) {
        state.currentLocaleCode = code;
      }
    }
  });

  test("renders", () => {
    const wrapper = shallowMount(Toolbar, {
      mocks: {
        $store: store,
        $i18n: {}
      }
    });

    // Default setup shows first locale.
    expect(wrapper.text()).toContain("Corpus");
    expect(wrapper.text()).toContain("Christi");
    console.log("BEFORE", wrapper.find("#cur-locale").text());
    expect(wrapper.find("#cur-locale").text()).toContain(flagForCountry("US"));

    // Switch locales.
    wrapper.vm.setCurrentLocale(testLocales[1]);
    console.log("AFTER", wrapper.find("#cur-locale").text());
    expect(wrapper.find("#cur-locale").text()).toContain(flagForCountry("EC"));
  });
});
