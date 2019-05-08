import { unique_id } from '../../support/helpers';

let team = unique_id();

describe("Create Team Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to teams page", function() {
    cy.visit("/teams");
  });

  it("WHEN: Event planner creates a new team", function() {
    cy.get("[data-cy=add-team]").click();

    cy.get("[data-cy=description]").type(team);

    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: A new team is listed", function() {
    cy.get("[data-cy=table-search]").clear().type(team);
    cy.get("tbody").contains(team);
  });

  it("AND: Event planner creates a blank team", function() {
    cy.get("[data-cy=add-team]").click();

    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: TeamForm has errors", function() {
    // Check for the validation error message
    cy.get(".v-messages__message").should("exist");
  });
});
