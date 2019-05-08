import { unique_id } from '../../support/helpers';

let course = unique_id();

describe("Archive Course", () => {
  before(() => {
    cy.login();
    cy.visit("/courses");
  });
  it("GIVEN: New Course", () => {
    cy.get("[data-cy=new-course]").click();
    cy.get("[data-cy=name]").type(course);
    cy.get("[data-cy=description]").type("Description");
    cy.get("[data-cy=save]").click();
  });
  it("WHEN: Clicking archive button", () => {
    cy.get("[data-cy=table-search]").type(course);
    cy.get("[data-cy=archive-toggle]").click();
    cy.get("[data-cy=confirm-archive]").click();
  });
  it("THEN: Check for archived course", () => {
    cy.get('.v-text-field--solo > .v-input__control > .v-input__slot').click()//switch from active to archive
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile').click()//select archive in drop down
    cy.get("[data-cy=table-search]").clear().type(course);
    cy.get("tbody").contains(course);
  });
});

describe("Unarchive Course", () => {
  it("GIVEN: Archived Course", () => {
    cy.get("[data-cy=table-search]").clear().type(course);
    cy.get("tbody").contains(course);
  });
  it("WHEN: Unarchiving course", () => {
    cy.get('[data-cy=archive-toggle]').click();
  });
  it("Check that course is now active", () => {
    cy.get('.v-text-field--solo > .v-input__control > .v-input__slot').click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
    cy.get("[data-cy=table-search]").clear().type(course);
    cy.get("tbody").contains(course);
  });
});
