import Account from "../models/Account";
import { Locale } from "../models/Locale.ts";
import { cloneDeep } from "lodash";

export const objectMap = {
  Account: Account,
  Locale: Locale
};

export const persistedStateOptions = {
  overwrite: true,
  getState(key, storage) {
    let value, states;
    states =
      (value = storage.getItem(key)) !== "undefined"
        ? JSON.parse(value)
        : undefined;
    for (let state in states) {
      let stateValue = states[state];
      if (Object.hasOwnProperty.call(stateValue, "__class__")) {
        if (!(stateValue.__class__ in objectMap))
          throw new Error(
            `class name ${stateValue.__class__} is not in objectMap`
          );
        let c = objectMap[stateValue.__class__]; // the class constructor
        if (!Object.hasOwnProperty.call(c, "fromObject"))
          throw new Error(
            `Class with mapped key ${
              stateValue.__class__
            } does not have 'fromObject' static method`
          );
        delete stateValue.__class__;
        let classState = c.fromObject(stateValue);
        states[state] = classState;
      }
    }
    return states;
  },
  setState(key, states, storage) {
    let encodedStates = {};
    for (let state in states) {
      let encodedState = cloneDeep(states[state]); // make a copy
      let c;
      if (
        (c = Object.values(objectMap).find(
          element => states[state] instanceof element
        ))
      ) {
        encodedState.__class__ = c.name; // store the class's name
      }
      encodedStates[state] = encodedState;
    }
    return storage.setItem(key, JSON.stringify(encodedStates));
  }
};
