/**
 * @file
 * @name filters.js
 * Filters.
 * Runs from 'main.ts'
 */
import Vue from "vue";
import moment from "moment";

Vue.filter("formatDate", (str) =>
  moment(String(str)).format("MM/DD/YYYY hh:mm")
);
