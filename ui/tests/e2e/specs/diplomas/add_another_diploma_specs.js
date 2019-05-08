import { unique_id } from '../../support/helpers';

let diploma_title_1 = unique_id();
let diploma_title_2 = unique_id();
let diploma_title_3 = unique_id();

describe("Get to Diplomas Page", () => {
  it("GIVEN: Successfull login", () => {
    cy.login();
  });
  it("WHEN: Clicking to diplomas page", () => {
    cy.deploma_page();
  });
  it("THEN: Should be in diplomas page", () => {
    cy.url().should("include", "/diplomas");
  });
});

describe("Fill out new diploma form and add another", () => {
  it("GIVEN: Form is loaded", () => {
    cy.get("[data-cy=diplomas-table-new]").click();
  });

  it("WHEN: Fill-out new diploma form", () => {
    cy.get("[data-cy=diplomas-form-name]").type(diploma_title_1); // Title
    cy.get("[data-cy=diploma-form-description]").type("Epic Dance Party"); // Description
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile").click(); // Select an item from the drop down
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile").click(); // Select another item from the drop down
  });

  it("THEN: Test add another button", () => {
    cy.get("[data-cy=form-addanother]").click();
    
  });
});

describe("Search for add another diploma", () => {
  it("GIVEN: diploma Page", () => {
    cy.get("[data-cy=cancel-new-diploma]").click();
  });

  it("WHEN: Searching for diploma", () => {
    cy.get("[data-cy=diplomas-table-search]").type(diploma_title_1);
    cy.get("tbody > tr > :nth-child(1)").contains(diploma_title_1);
  });

describe("Add two diplomas with add another button", () => {
  it("GIVEN: Form is loaded", () => {
    cy.get("[data-cy=diplomas-table-new]").click();
  });

  it("WHEN: Fill-out new diploma form", () => {
    cy.get("[data-cy=diplomas-form-name]").type(diploma_title_2); // Title
    cy.get("[data-cy=diploma-form-description]").type("Epic Dance Party"); // Description
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile").click(); // Select an item from the drop down
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile").click(); // Select another item from the drop down
  });

  it("THEN: Test add another button", () => {
    cy.get("[data-cy=form-addanother]").click();
  });

  it("THEN: Fill-out and save another", () => {
    cy.get("[data-cy=diplomas-form-name]").type(diploma_title_3); // Title
    cy.get("[data-cy=diploma-form-description]").type("Epic Dance Party"); // Description
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile").click(); // Select an item from the drop down
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile").click(); // Select another item from the drop down
  });

  it("THEN: Test add another button", () => {
    cy.get("[data-cy=form-addanother]").click(); // Add another button
    cy.get("[data-cy=cancel-new-diploma]").click(); // Cancel button
  });

  it("THEN: Search for the first one", () => {
    cy.get("[data-cy=diplomas-table-search]").clear();
    cy.get("[data-cy=diplomas-table-search]").type(diploma_title_2); // Go to search bar
    cy.get("tbody > tr > :nth-child(1)").contains(diploma_title_2); // Find the first item and check if it matches
  });

  it("THEN: Search for the seccond one", () => {
    cy.get("[data-cy=diplomas-table-search]").clear()
    cy.get("[data-cy=diplomas-table-search]").type(diploma_title_3); // Go to search bar
    cy.get("tbody > tr > :nth-child(1)").contains(diploma_title_3); // Find the first item and check if it matches
  });
});

});
