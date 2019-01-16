// https://docs.cypress.io/api/introduction/api.html

describe("Admin edits user settings", function() {
  it("GIVEN: Admin loads PersonTable", function() {
    cy.visit("/login");
    cy.get("[data-cy=username]").type("Cytest");
    //Enters the password
    cy.get("[data-cy=password]").type("password");
    //Clicks the log in button
    cy.get("[data-cy=login]").click();
    cy.url().should("include", "/admin");
    //open nav drawer
    cy.get("[data-cy=toggle-nav-drawer]").click();
    //goes to the people page
    cy.get("[data-cy=people]").click();
    cy.get("[data-cy=search]").type("Quality");
  });
  it("WHEN: Clicking on the edit button", () => {
    cy.get("[data-cy=edit-person").click();
  });
  it("THEN: The person's information can be cleared", () => {
    cy.get("[data-cy=clear").click();
  });
  it("AND: The person's Name can be entered", () => {
    cy.get("[data-cy=first-name]").type("Quality");
    cy.get("[data-cy=last-name]").type("Assurance");
  });
  it("AND: The person's gender can be checked", () => {
    cy.get("[data-cy=radio-gender]").within(() => {
      cy.get(".v-label")
        .last()
        .click();
      cy.get(".v-label")
        .first()
        .click();
    });
  });
  it("AND: The person's birthday can be entered", () => {
    cy.get("[data-cy=birthday]").click();
    cy.contains("5").click();
  });
  it("AND: The person's email & phone # can be entered", () => {
    cy.get("[data-cy=email]").type("test@aol.com");
    cy.get("[data-cy=phone]").type("1113334444");
  });
  it("FINALLY: The person's new information can be saved", () => {
    cy.get("[data-cy=save]").click();
  });
});
