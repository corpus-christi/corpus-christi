import { unique_id } from '../../support/helpers';

let event = unique_id();

describe("Duplicate Event Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Events Page", function() {
    cy.visit("/events");
  });

  it("WHEN: Event planner duplicates an event", function() {
    cy.get("[data-cy=duplicate]")
      .eq(0)
      .click();

    // Rename
    cy.get("[data-cy=title]").clear().type(event);
    // Pick a new start and end date
    cy.get("[data-cy=start-date-menu]").click();
    // Get cypress to click on a certain position on the calendar
    cy.get("[data-cy=start-date-picker] > .v-picker__body > :nth-child(1) > .v-date-picker-header > :nth-child(3").click();
    cy.get(
      "[data-cy=start-date-picker] > .v-picker__body > :nth-child(1) > .v-date-picker-table > .tab-transition-enter-active > tbody > :nth-child(5) > :nth-child(1) > .v-btn > .v-btn__content"
    ).click();

    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: A new event is created", function() {
    cy.get("[data-cy=table-search]").clear().type(event);
    cy.get("tbody").contains(event);
  });
});
