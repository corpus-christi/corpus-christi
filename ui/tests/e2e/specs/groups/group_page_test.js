describe("tests going to the group page", () => {
  it("goes to the group page", () => {
    cy.login();
    cy.visit("/groups");
    cy.url().should("include", "/groups/all");
  });
});
