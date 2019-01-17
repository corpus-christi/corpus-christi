describe("Get to Courses Page", () => {
    it("Given Successfull login", () => {
      cy.visit("/");
      cy.get("[data-cy=account-button]").click();
      cy.get("[data-cy=username]").type("lpratico");
      cy.get("[data-cy=password]").type("Qwerty1234");
      cy.get("[data-cy=login]").click();
    });
  
    it("When: clicking to course page", () => {
      cy.get("[data-cy=open-navigation]").click();
      cy.get('[data-cy=courses-admin]').click();
    });
    it("Then: should be in course page", () => {
      cy.url().should("include", "/courses");
    });
});

describe("Flip through Courses Page", () => {
    it("Next page", () => {
        cy.get('[aria-label="Siguiente página"]').click()
    });
    it("back page", () => {
        cy.get('[aria-label="Pagina anterior"]').click()
    });
});