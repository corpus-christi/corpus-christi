describe("Get to Courses Page", () => {
    it("Given Successfull login", () => {
      cy.login()
    });
  
    it("When: clicking to course page", () => {
      cy.get("[data-cy=open-navigation]").click();
      cy.get('[data-cy=courses-admin]').click();
    });
    it("Then: should be in course page", () => {
      cy.url().should("include", "/courses");
    });
  });

  describe('cancels Course Form', ()=>{
    it('Given: New Course Form', () =>{
      cy.get('[data-cy=courses-table-new]').click()
    });
    it('When: Form is filled out', ()=>{
      cy.get('[data-cy=course-form-name]').type('COS 5')
      cy.get('[data-cy=course-form-description]').type('Hello World')
    });
    it('Then: cancel clear button', ()=>{
        cy.get('[data-cy=course-editor-actions] > .secondary--text').click()
        cy.url().should("include", "/courses")
    });
});