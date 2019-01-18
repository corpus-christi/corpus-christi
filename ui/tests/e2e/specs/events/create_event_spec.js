describe("Create Event Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event Planner goes to Event page", function() {
    cy.visit("/events/all");
  });

  it("WHEN: Event Planner adds a new event and fills out details correctly", function() {
    cy.get("[data-cy=add-event]").click();
    cy.get("[data-cy=title]").type("New Event");

    cy.get("[data-cy=description]").type("A neat description of something.");

    // Get first location in the search
    cy.get("[data-cy=entity-search-field]").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();

    cy.get("[data-cy=start-date-menu]").click();
    // Get cypress to click on a certain position on the calendar
    cy.get(
      "tbody > :nth-child(5) > :nth-child(1) > .v-btn > .v-btn__content"
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

  it("THEN: A new event is listed in the table", function() {
    // Switch to see all events on one page
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot"
    ).click();
    cy.contains("Todos").click();

    cy.get("tbody").contains("New Event");
  });

  it("WHEN: Event planner adds a new event and fills out a blank form", function() {
    cy.get("[data-cy=add-event]").click();
    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: Error messages appear", function() {
    // Check for error messages under each input field
    cy.get(
      "form > :nth-child(1) > .v-input__control > .v-text-field__details > .v-messages > .v-messages__wrapper > .v-messages__message"
    ).should("exist");
    cy.get(
      "[data-cy=start-date-menu] > .v-menu__activator > .v-input > .v-input__control > .v-text-field__details > .v-messages > .v-messages__wrapper > .v-messages__message"
    ).should("exist");
    cy.get(
      "[data-cy=start-time-dialog] > .v-dialog__activator > .v-input > .v-input__control > .v-text-field__details > .v-messages > .v-messages__wrapper > .v-messages__message"
    ).should("exist");
    cy.get(
      "[data-cy=start-time-dialog] > .v-dialog__activator > .v-input > .v-input__control > .v-text-field__details > .v-messages > .v-messages__wrapper > .v-messages__message"
    ).should("exist");

    cy.get("[data-cy=form-cancel]").click();
  });
});
