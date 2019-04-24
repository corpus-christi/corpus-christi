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

describe("cancels Course Form", () => {
  it("GIVEN: New Course Form", () => {
    cy.get("[data-cy=new-course]").click();
  });
  it("WHEN: Form is filled out", () => {
    cy.get("[data-cy=name]").type("Test");
    cy.get("[data-cy=description]").type("Hello World");
  });
  it("THEN: cancel clear button", () => {
    cy.get("[data-cy=actions] > .secondary--text").click();
    cy.url().should("include", "/courses");
  });
});
