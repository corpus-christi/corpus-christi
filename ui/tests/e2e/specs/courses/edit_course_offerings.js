import { unique_id } from '../../support/helpers';

let description = unique_id();
let description2 = unique_id();

describe("Get to details of a course", () => {
  before(() => {
    cy.login();
    cy.visit("/courses");
  });
  it("GIVEN: Course Details", () => {
    cy.get("[data-cy=table-search]").clear().type("Alone");
    cy.get("tbody").contains("Alone").click();
    cy.url().should("include", "/courses/");
  });
  it("WHEN: Creating new course section", () => {
    cy.get("[data-cy=new-offering]").click();
    cy.get("[data-cy=offering-description]").type(description);
    cy.get("[data-cy=offering-size]").type(27);
    cy.get("[data-cy=save-offering]").click();
  });
  it("THEN: Edit existing course section", () => {
    cy.get("[data-cy=edit-offering]").eq(0).click();
    cy.get("[data-cy=offering-description]").clear().type(description2);
    cy.get("[data-cy=offering-size]").clear().type(16);
    cy.get("[data-cy=save-offering]").click();
  });
  it("AND: Check if edited", () => {
    cy.get("[data-cy=offering-search]").clear().type(description2);
    cy.get("tbody").contains(description2);
  });
});