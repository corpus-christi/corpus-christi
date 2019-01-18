describe("Get to Diplomas Page", () => {
    it("Given Successfull login", () => {
      cy.login();
    });
  
    it("When: clicking to diplomas page", () => {
      cy.get("[data-cy=open-navigation]").click();
      cy.get('[data-cy=diplomas-admin]').click();
    });
    it("Then: should be in diplomas page", () => {
      cy.url().should("include", "/diplomas");
    });
  });