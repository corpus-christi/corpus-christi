import { unique_id } from '../../support/helpers';

var course = unique_id();

describe("Edit Course", () => {
  before(() => {
    cy.login();
    cy.visit("/courses");
  });
  it("GIVEN: Course Form", () => {
    cy.get("[data-cy=edit]").eq(0).click();
  });
  it("WHEN: Editing course", () => {
    cy.get("[data-cy=name]")
      .clear()
      .type(course);
    cy.get("[data-cy=description]").clear().type("Description");
    cy.get('[data-cy=prerequisites]').click();
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(1)').click();
  });
  it("THEN: Changes are saved", () => {
    cy.get("[data-cy=save]").click();
    cy.get("[data-cy=table-search]").type(course);
    cy.get("tbody").contains(course);
  });
});
