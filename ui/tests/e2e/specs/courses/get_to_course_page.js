describe("Get to Courses Page", () => {
    it("Given: Successfull login", () => {
      cy.login()
    });
  
    it("When: clicking to course page", () => {
      cy.get('[data-cy=toggle-nav-drawer]').click();
      cy.get('[data-cy=courses-admin]').click();
    });
    it("Then: should be in course page", () => {
      cy.url().should("include", "/courses");
    });
  });