/**
 * @file
 * @name filters.js
 * @exports main.ts
 * Filters.
 */
import Vue from "vue";
import moment from "moment";

Vue.filter("formatDate", (str) =>
  moment(String(str)).format("MM/DD/YYYY hh:mm")
);
