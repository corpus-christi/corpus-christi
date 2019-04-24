import { unique_id } from '../../support/helpers';

let course = unique_id();

describe("Get to Courses Page", () => {
  it("GIVEN Successful login", () => {
    cy.login();
  });

  it("WHEN: clicking to course page", () => {
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=courses]").click();
  });
  it("THEN: should be in course page", () => {
    cy.url().should("include", "/courses");
  });
});

describe("search for courses that exist", () => {
  it("WHEN: course name is typed", () => {
    cy.get("[data-cy=table-search]").type("Alone low investment");
  });
  it("THEN: should find course name", () => {
    cy.get("tbody").contains("Alone low investment");
  });
});

describe("search for courses that does not exist", () => {
  it("WHEN: course name is typed", () => {
    cy.get("[data-cy=table-search]")
      .clear()
      .type(course);
  });
  it("THEN: should find nothing", () => {
    cy.get("tbody > :nth-child(1)").contains(
      "No se encontraron registros coincidentes"
    );
  });
});
