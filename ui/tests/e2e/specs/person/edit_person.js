import { unique_name, unique_email, unique_phone } from '../../support/helpers';

let first = unique_name();
let last = unique_name();
let email = unique_email();
let phone = unique_phone();

describe("Admin edits user information", function() {
  before(() => {
    cy.login();
    cy.visit("/people");
  });
  it("GIVEN: The Edit User form:", function() {
      cy.get("[data-cy=edit-person]").eq(0).click();
  });
  it("WHEN: Editing the information", function() {
    cy.get("[data-cy=first-name]")
      .clear()
      .type(first);
    cy.get("[data-cy=last-name]")
      .clear()
      .type(last);
    cy.get("[data-cy=email]")
      .clear()
      .type(email); //email
    cy.get("[data-cy=phone]")
      .clear()
      .type(phone); //phone
    cy.get("[data-cy=radio-gender]").within(() => {
      cy.get(".v-label")
        .first()
        .click(); //Male
    });
    cy.get("[data-cy=next]").click();
    cy.get("[data-cy=save]").click();
  });
  it("THEN: Verfiy the user was edited", function() {
  cy.get("[data-cy=search]")
    .clear()
    .type(first);
  cy.get("[data-cy=person-table").within(() => {
    cy.get("tbody > :nth-child(1) > :nth-child(2)").should(
      "contain",
      first
    );
    cy.get("tbody > :nth-child(1) > :nth-child(3)").should(
      "contain",
      last
    );
    cy.get("tbody > :nth-child(1) > :nth-child(4)").should(
      "contain",
      email
    );
    cy.get("tbody > :nth-child(1) > :nth-child(5)").should(
      "contain",
      phone
    );
    });
  });
});
