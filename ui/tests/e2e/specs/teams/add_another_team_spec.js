import { unique_id } from '../../support/helpers';

let team1 = unique_id();
let team2 = unique_id();
let team3 = unique_id();

describe("Create Team Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to teams page", function() {
    cy.visit("/teams");
  });

  it("WHEN: Event planner adds three teams", function() {
    cy.get("[data-cy=add-team]").click();

    cy.get("[data-cy=description]").type(team1);
    cy.get("[data-cy=form-add-another]").click();
    cy.get("[data-cy=description]").type(team2);
    cy.get("[data-cy=form-add-another]").click();
    cy.get("[data-cy=description]").type(team3);
    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: Each new team is created", function() {
    cy.get("[data-cy=table-search]").clear().type(team1);
    cy.get("tbody").contains(team1);
    cy.get("[data-cy=table-search]").clear().type(team2);
    cy.get("tbody").contains(team2);
    cy.get("[data-cy=table-search]").clear().type(team3);
    cy.get("tbody").contains(team3);
  });
});
