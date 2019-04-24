import { unique_id } from '../../support/helpers';

let course = unique_id();

describe("Get to Courses Page", () => {
  it("GIVEN: Successful login", () => {
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

describe("Add Course", () => {
  it("GIVEN: New Course Form", () => {
    cy.get("[data-cy=new-course]").click();
  });
  it("WHEN: Form is filled out", () => {
    cy.get("[data-cy=name]").type(course);
    cy.get("[data-cy=description]").type("Hello World");
  });
  it("THEN: Click save button", () => {
    cy.get("[data-cy=save]").click();
  });
});

describe("Archive Course", () => {
  it("Click archive button", () => {
    cy.get("[data-cy=table-search]").type(course);
    cy.get("[data-cy=archive-toggle]").click(); //click archive
    cy.get("[data-cy=confirm-archive]").click(); //confirm click
  });
  it("View archived Courses", () => {
    cy.get('.v-text-field--solo > .v-input__control > .v-input__slot').click()//switch from active to archive
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile').click()//select archive in drop down
    cy.get("tbody > tr > :nth-child(1)").contains(course);
  });
});

describe("Unarchive Course", () => {
  it("Click unarchive button", () => {
    cy.get('[data-cy=archive-toggle]').click();
  });
  it("Return to active courses", () => {
    cy.get('.v-text-field--solo > .v-input__control > .v-input__slot').click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
    cy.get("tbody > tr > :nth-child(1)").contains(course);
  });
});
