describe("Admin Login Test", function () {
  it("GIVEN: Click on Account bubble", function () {
    cy.visit("/");
    cy.get("[data-cy=account-button]").click();
    cy.url().should("include", "/login");
  });
  //Switch to English
  it("WHEN: Clicks the language button", () => {
    cy.get("[data-cy=cur-locale]").click();
  });
  it("WHEN: Switches the language", () => {
    cy.get("[data-cy=language-dropdown]").click('center');
  });
  //Login
  it("WHEN: Providing correct login credentials", function () {
    cy.get("[data-cy=username]").type("Cytest");
    cy.get("[data-cy=password]").type("password");
    cy.get("[data-cy=login]").click();
  });
  //Open navigate drawer & go to group
  it("WHEN: Switch to Group Page", function () {
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=groups]").click();
    cy.location('pathname')
      .should('include', '/groups/all');
  })
  it("WHEN: Test line graph", function () {
    cy.wait(1000).get('*[class^="shrink col"]').eq(1).click();
    cy.get('*[class^="v-list-item__content"]').contains(" Show Line Graph ").click()
    cy.get('*[class^="v-input__icon v-input__icon--append"]').eq(1).click()
    cy.wait(3000).get('*[class^="v-list-item__title d-flex justify-center"]').contains("Select All").click();
    cy.get('*[class^="v-input__icon v-input__icon--append"]').eq(1).click()
    cy.get('*[class^="v-toolbar__content"]').eq(1).click("right");
    cy.get('*[class^="v-input__icon v-input__icon--append"]').eq(0).click();
    cy.wait(3000).get('*[class^="v-list-item__title"]').contains("Weekly").click();

  })
})
