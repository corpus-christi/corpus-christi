describe("Get to Courses Page", () => {
  it("GIVEN: Successful login", () => {
    cy.login();
  });

  it("WHEN: clicking to course page", () => {
    cy.course_page();
  });
  it("THEN: should be in course page", () => {
    cy.url().should("include", "/courses");
  });
});
