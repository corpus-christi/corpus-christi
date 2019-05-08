import { unique_id } from '../../support/helpers';

let course1 = unique_id();
let course2 = unique_id();
let course3 = unique_id();

describe("Add Course", () => {
  before(() => {
    cy.login();
    cy.visit("/courses");
  });
  it("GIVEN: New Course Form", () => {
    cy.get("[data-cy=new-course]").click();
  });
  it("WHEN: Form is filled out", () => {
    cy.get("[data-cy=name]").type(course1);
    cy.get("[data-cy=description]").type("Hello World");
  });
  it("THEN: Click save button", () => {
    cy.get("[data-cy=save]").click();
    cy.get("[data-cy=table-search]").type(course1);
    cy.get("tbody").contains(course1);
  });
});

describe("Attempt to Add Course Without Title", () => {
  it("GIVEN: New Course Form", () => {
    cy.get("[data-cy=new-course]").click();
  });
  it("WHEN: Just Title is filled out", () => {
    cy.get("[data-cy=description]").type("Description");
  });
  it("THEN: Click save button", () => {
    cy.get("[data-cy=save]").click();
  });
  it("AND: Validation fails", () => {
    cy.wait(100);
    cy.get(".v-messages__message").should("exist");
    cy.get("[data-cy=cancel]").click();
  });
});

describe("Add Course with a Prereq", () => {
  it("GIVEN: New Course Form", () => {
    cy.get("[data-cy=new-course]").click();
  });
  it('WHEN: Form is filled out', ()=>{
    cy.get('[data-cy=name]').type(course2)
    cy.get('[data-cy=description]').type('Hello World')
    cy.get('[data-cy=prerequisites]').click();
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(1)').click();
  });
  it("THEN: Click save button", () => {
    cy.get("[data-cy=save]").click();
    cy.get("[data-cy=table-search]")
      .clear()
      .type(course2);
    cy.get("tbody").contains(course2);
  });
});

describe("Add Course with Muiltiple Prereq", () => {
  it("GIVEN: New Course Form", () => {
    cy.get("[data-cy=new-course]").click();
  });
  it("WHEN: Form is filled out", () => {
    cy.get("[data-cy=name]").type(course3);
    cy.get("[data-cy=description]").type("Hello World");
    cy.get('[data-cy=prerequisites]').click();
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(1)').click();
    cy.get('[data-cy=prerequisites]').click();
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(2)').click();
    cy.get('[data-cy=prerequisites]').click();
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(2)').click();
  });
  it("THEN: Click save button", () => {
    cy.get("[data-cy=save]").click();
    cy.get("[data-cy=table-search]")
      .clear()
      .type(course3);
    cy.get("tbody").contains(course3);
  });
});