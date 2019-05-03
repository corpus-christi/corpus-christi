import { unique_id } from '../../support/helpers';

let event1 = unique_id();
let event2 = unique_id();

describe("Add Another Event Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Events Page", function() {
    cy.visit("/events");
  });

  it("WHEN: Adding Two Events", function() {
    cy.get("[data-cy=add-event]").click();

    // Add Event 1
    cy.get("[data-cy=title]").type(event1);

    cy.get("[data-cy=description]").type("Description");

    // Get first location in the search
    cy.get("[data-cy=entity-search-field]").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();

    cy.get("[data-cy=start-date-menu]").click();
    // Get cypress to click on a certain position on the calendar
    cy.get("[data-cy=start-date-picker] > .v-picker__body > :nth-child(1) > .v-date-picker-header > :nth-child(3").click();
    cy.get(
      "[data-cy=start-date-picker] > .v-picker__body > :nth-child(1) > .v-date-picker-table > .tab-transition-enter-active > tbody > :nth-child(5) > :nth-child(1) > .v-btn > .v-btn__content"
    ).click();

    cy.get("[data-cy=start-time-dialog]").click();
    // Cypress clicks a style position for hour
    cy.get('[style="left: 76.8468%; top: 34.5%;"]').click();
    // Click randomly for minute
    cy.get(".v-time-picker-clock__inner")
      .eq(1)
      .click();

    cy.get("[data-cy=start-time-ok]").click();
    cy.get("[data-cy=end-date-menu]").click();
    // Get cypress to click on a certain position on the calendar
    cy.get(
      "[data-cy=end-date-picker] > .v-picker__body > :nth-child(1) > .v-date-picker-table > table > tbody > :nth-child(5) > :nth-child(1) > .v-btn > .v-btn__content"
    ).click();

    cy.get("[data-cy=end-time-dialog]").click();
    // Cypress clicks a style position for hour
    cy.get('[style="left: 76.8468%; top: 65.5%;"]').click();
    // Click randomly for minute
    cy.get(".v-time-picker-clock__inner")
      .eq(1)
      .click();
    cy.get("[data-cy=end-time-ok]").click();

    // Add Another Event
    cy.get("[data-cy=form-add-another]").click();
    // Add Event 2
    cy.get("[data-cy=title]").type(event2);

    cy.get("[data-cy=description]").type("Description");

    // Get first location in the search
    cy.get("[data-cy=entity-search-field]").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();

    cy.get("[data-cy=start-date-menu]").click();
    // Get cypress to click on a certain position on the calendar
    cy.get("[data-cy=start-date-picker] > .v-picker__body > :nth-child(1) > .v-date-picker-header > :nth-child(3").click();
    cy.get(
      "[data-cy=start-date-picker] > .v-picker__body > :nth-child(1) > .v-date-picker-table > .tab-transition-enter-active > tbody > :nth-child(5) > :nth-child(1) > .v-btn > .v-btn__content"
    ).click();

    cy.get("[data-cy=start-time-dialog]").click();
    // Cypress clicks a style position for hour
    cy.get('[style="left: 76.8468%; top: 34.5%;"]').click();
    // Click randomly for minute
    cy.get(".v-time-picker-clock__inner")
      .eq(1)
      .click();

    cy.get("[data-cy=start-time-ok]").click();
    cy.get("[data-cy=end-date-menu]").click();
    // Get cypress to click on a certain position on the calendar
    cy.get(
      "[data-cy=end-date-picker] > .v-picker__body > :nth-child(1) > .v-date-picker-table > table > tbody > :nth-child(5) > :nth-child(1) > .v-btn > .v-btn__content"
    ).click();

    cy.get("[data-cy=end-time-dialog]").click();
    // Cypress clicks a style position for hour
    cy.get('[style="left: 76.8468%; top: 65.5%;"]').click();
    // Click randomly for minute
    cy.get(".v-time-picker-clock__inner")
      .eq(1)
      .click();
    cy.get("[data-cy=end-time-ok]").click();
    
    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: The New Events are Created", function() {
    cy.get("[data-cy=table-search]").clear().type(event1);
    cy.get("tbody").contains(event1);
    cy.get("[data-cy=table-search]").clear().type(event2);
    cy.get("tbody").contains(event2);
  });
});

