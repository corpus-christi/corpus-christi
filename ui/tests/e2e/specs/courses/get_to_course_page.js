describe("Get to Courses Page", () => {
  it("Given: Successfull login", () => {
    cy.login();
  });

  it("When: clicking to course page", () => {
    cy.course_page();
  });
  it("Then: should be in course page", () => {
    cy.url().should("include", "/courses");
  });
});
