import { unique_id } from '../../support/helpers';

let course1 = unique_id();
let course2 = unique_id();
let course3 = unique_id();

describe("Create Courses with Add Another button", () => {
  before(() => {
    cy.login();
    cy.visit("/courses");
  });
  it("GIVEN: New Course Form", () => {
    cy.get("[data-cy=new-course]").click();
  });
  it("WHEN: Adding multiple courses", () => {

    cy.get("[data-cy=name]").type(course1);
    cy.get("[data-cy=description]").type("Description1");
    cy.get("[data-cy=add-another]").click();
    cy.get("[data-cy=name]").type(course2);
    cy.get("[data-cy=description]").type("Description2");
    cy.get("[data-cy=add-another]").click();
    cy.get("[data-cy=name]").type(course3);
    cy.get("[data-cy=description]").type("Description3");
  });
  it("THEN: Click save button", () => {
    cy.get("[data-cy=save]").click();
  });
  it("AND: Verify courses were added successfully", () => {
    cy.get("[data-cy=table-search]").clear().type(course1);
    cy.get("tbody").contains(course1);
    cy.get("[data-cy=table-search]").clear().type(course2);
    cy.get("tbody").contains(course2);
    cy.get("[data-cy=table-search]").clear().type(course3);
    cy.get("tbody").contains(course3);
  });
});