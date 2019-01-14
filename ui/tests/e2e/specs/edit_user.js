// https://docs.cypress.io/api/introduction/api.html

describe("Testing Editing User Information", () => {
  it("Given: Visits the app root url, logs into an account, navigates" +
    "to the people page, and filters the search to one person", () => {
    cy.visit("/");
    //Clicks on the Account button
    cy.get('[data-cy=account-button]')
      .click();
    //Enters the Username
    cy.get('[data-cy=username]')
      .type('Cytest');
    //Enters the password
    cy.get('[data-cy=password]')
      .type('password');
    //Clicks the log in button
    cy.get('[data-cy=login]')
      .click();
    //Making sure we're in the right place
    cy.url().should('include', '/admin');
    //open nav drawer
    cy.get('[data-cy=open-navigation]')
      .click();
    //goes to the people page
    cy.get('[data-cy=people]')
      .click();
    cy.get('[data-cy=search]')
      .type('Quality');
  });
  it("When: Clicking on the edit button", () => {
    cy.get("[data-cy=edit-person").click();
  });
  it("Then: The person's information can be cleared", () => {
    cy.get("[data-cy=clear").click();
  });
  it("And: The person's Name can be entered", () => {
    cy.get("[data-cy=first-name]").type("Quality");
    cy.get("[data-cy=last-name]").type("Assurance");
  });
  it("And: The person's gender can be checked", () => {
    //TODO:
    //cy.get('[data-cy=radio-gender]').find("[data-cy=radio-m]").check();
  });
  it("And: The person's birthday can be entered", () => {
    cy.get("[data-cy=birthday]").click();
    cy.contains("5").click();
  });
  it("And: The person's email & phone # can be entered", () => {
    cy.get("[data-cy=email]").type("test@aol.com");
    cy.get("[data-cy=phone]").type("1113334444");
  });
  it("Finally: The person's new information can be saved", () => {
    cy.get("[data-cy=save]").click();
  });
});
