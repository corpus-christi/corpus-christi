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
  });
  it("WHEN: Test ascending/descending sort ", function () {
    for(let i =0; i< 5; i++){
      cy.wait(1000).get('tr>th').eq(i).click().click().click();
    }
  });
  it("WHEN: Test drop down menu", function () {
    cy.get('*[class^="col col-3"]').click()
    cy.get(".v-menu__content").contains("View Active").click()
    cy.get('*[class^="col col-3"]').click()
    cy.get(".v-menu__content").contains("View Archived").click()
    cy.get('*[class^="col col-3"]').click()
    cy.get(".v-menu__content").contains("View All").click()
  })
  it("WHEN: Add a group", function () {
    cy.wait(1000).get('*[class^="shrink col col-4"]').click("left");
    cy.get("[role=menuitem]").first().click();
    cy.get("[data-cy=title]").type("Test Group")
    cy.get("[data-cy=description]").type("Test Group Description")
    cy.get('*[class^="v-btn__content"]').contains(" Create a new Group Type ").click()
    cy.get("[type=text]").eq(5).type("Cypress Test Group")
    cy.get('*[class^="v-btn__content"]').contains("Save").click()
    cy.get('*[class^="v-btn__content"]').contains("Save ").click()
    cy.get("[data-cy=form-search]").type("Test Group").wait(2000).clear();
  })
  it("WHEN: Test search bar", function () {
    cy.get("[data-cy=form-search]").type("Cel").wait(2000).clear();
  })
  it("WHEN: Test search bar", function () {
    cy.wait(1000).get("[data-cy=duplicate]").first().click();
    cy.get("[data-cy=form-save]").click();
  })
  it("WHEN: Test archive button", function () {
    cy.wait(1000).get("[data-cy=archive]").first().click();
    cy.get("[data-cy=confirm-archive]").click();
  })
  it("WHEN: Test Edit Group", function () {
    cy.wait(1000).get("[data-cy=edit]").first().click();
    cy.get("[data-cy=title]").clear().type("Test Group")
    cy.get("[data-cy=description]").clear().type("Test Group Description")
    cy.get('*[class^="v-btn__content"]').contains("Save ").click()
  })
  it("WHEN: Split a group", function () {
    cy.wait(1000).get("[data-cy=split]").last().click();
    cy.get("[name=child-title]").clear().type("Test Group Name")
    cy.get("[name=child-description]").clear().type("Test Group Description")
    cy.get("[data-cy=entity-search-field]").eq(2).click()
    cy.get("[role=option]").last().click()
    cy.get('*[class^="v-btn__content"]').contains("Next").click()
    cy.wait(1000).get('*[class^="row no-gutters"]').eq(5).click('right')
    cy.wait(1000).get('*[class^="v-btn__content"]').contains("Confirm").click()
  })
});
