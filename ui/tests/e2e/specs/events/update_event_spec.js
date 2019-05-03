import { unique_id } from '../../support/helpers';

let event = unique_id();
let description = unique_id();

describe("Update Event Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event Page", function() {
    cy.visit("/events/all");
  });

  it("WHEN: Event Planner wants to update an event", function() {
    // Put a new title on the event
    cy.get("[data-cy=edit]")
      .eq(0)
      .click();
    cy.get("[data-cy=title]").clear().type(event);

    // Rewrite a new description of the event
    cy.get("[data-cy=description]").clear().type(description);

    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: Event title should be updated", function() {
    cy.get("[data-cy=table-search]").clear().type(event);
    cy.get("tbody").contains(event);
  });

  it("AND: The event description should be updated", function() {
    cy.get("[data-cy=edit]")
      .eq(0)
      .click();

    cy.get("[data-cy=description]").should(
      "have.value",
      description
    );
  });
});
