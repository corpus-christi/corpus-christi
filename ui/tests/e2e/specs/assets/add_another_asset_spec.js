import { unique_id } from '../../support/helpers';

let course1 = unique_id();
let course2 = unique_id();
let course3 = unique_id();

describe("Add Another Asset Test", function() {
  // Tests the add another button by using it's functionality once.
  before(() => {
    cy.login();
  });

  it("GIVEN: Assets page is loaded", function() {
    cy.visit("/assets");
  });

  it("WHEN: Form is loaded", function() {
    cy.get("[data-cy=add-asset]").click();
  });
    
  it("THEN: Fill out form", function() {
    cy.get("[data-cy=description]").type(course1);

    // Get the first location in the list
    cy.get("[data-cy=entity-search-field]").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click(); 
  });

  it("THEN: Add another is clicked and validated", function() {
    cy.get("[data-cy=add-another]").click();
    cy.get("[data-cy=form-cancel]").click();
    cy.get("[data-cy=form-search]").type(course1);
    cy.get("tbody").contains(course1);
  });
});



describe("Add Multiple Courses With Add Another Test", function() {
  // Tests the add another button by using it's functionality twice.
  it("WHEN: Form is loaded", function() {
    cy.get("[data-cy=add-asset]").click();
  });
    
  it("THEN: Add first course", function() {
    cy.get("[data-cy=description]").type(course2);
    // Get the first location in the list
    cy.get("[data-cy=entity-search-field]").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
    cy.get("[data-cy=add-another]").click();
  });

  it("THEN: Add seccond course", function() {
    cy.get("[data-cy=description]").type(course3);
    // Get the first location in the list
    cy.get("[data-cy=entity-search-field]").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
    cy.get("[data-cy=add-another]").click();
  });

  it("THEN: Courses are validated", function() {
    cy.get("[data-cy=form-cancel]").click();
    cy.get("[data-cy=form-search]").clear();
    cy.get("[data-cy=form-search]").type(course2);
    cy.get("tbody").contains(course2);
    cy.get("[data-cy=form-search]").clear();
    cy.get("[data-cy=form-search]").type(course3);
    cy.get("tbody").contains(course3);
  });
});