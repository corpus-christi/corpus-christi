import { unique_id } from '../../support/helpers';

var course_name = unique_id();

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

describe("Edit courses", () => {
  it("Open edit course", () => {
    cy.get(
      ":nth-child(1) > :nth-child(3) > .layout > :nth-child(1) > span > .v-btn"
    ).click();
  });
  it("change course title", () => {
    cy.get("[data-cy=name]")
      .clear()
      .type(course_name);
  });
  it("save changes", () => {
    cy.get("[data-cy=actions] > .primary").click();
    cy.get("[data-cy=save]").click();
    cy.get("[data-cy=table-search]").type(course_name);
    cy.get("tbody").contains(course_name);
  });
});
