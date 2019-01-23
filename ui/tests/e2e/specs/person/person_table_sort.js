// https://docs.cypress.io/api/introduction/api.html
//this is a bad test
//It uses hard coded expectations, however, they change every time ./reset-database is run
//Ideally I can come up with a way to fix this, but I currently don't have time.
//Sorry to whoever is reading this in hopes of running/fixing this test -AD
describe("Testing Editing User Information", () => {
  it(
    "Given: Visits the app root url, logs into an account, and navigates " +
      "to the people page",
    () => {
      cy.login();
      //Making sure we're in the right place
      cy.url().should("include", "/admin");
      //open nav drawer
      cy.get("[data-cy=toggle-nav-drawer]").click();
      //goes to the people page
      cy.get("[data-cy=people]").click();
    }
  );
  it("When: clicking on a sorting method: last name descending", () => {
    cy.get("[data-cy=person-table").within(() => {
      cy.get("thead > :nth-child(1) > :nth-child(3)").click();
    });
  });
  it("Then: The table should resort itself based on what was being sorted", () => {
    cy.get("[data-cy=person-table").within(() => {
      cy.get("tbody > :nth-child(1) > :nth-child(3)").contains("Arellano");
    });
  });

  it("And: When clicked again should change the sorting method: last name ascending", () => {
    cy.get("[data-cy=person-table").within(() => {
      cy.get("thead > :nth-child(1) > :nth-child(3)").click();
      cy.get("tbody > :nth-child(1) > :nth-child(3)").contains("Ziffle");
    });
  });
  it("And: When clicked again should change the sorting method: last name by user_id", () => {
    cy.get("[data-cy=person-table").within(() => {
      cy.get("thead > :nth-child(1) > :nth-child(3)").click();
      cy.get("tbody > :nth-child(1) > :nth-child(3)").contains("Brown");
    });
  });
  it("And: The other sorting buttons should be clickable and work as well", () => {
    cy.get("[data-cy=person-table").within(() => {
      cy.get("thead > :nth-child(1) > :nth-child(2)").click();
      cy.get("tbody > :nth-child(1) > :nth-child(2)").contains("Andrew");
      cy.get("thead > :nth-child(1) > :nth-child(4)")
        .click()
        .click();
      cy.get("tbody > :nth-child(1) > :nth-child(4)").contains(
        "xdiaz@industrias.com"
      );
      cy.get("thead > :nth-child(1) > :nth-child(5)").click();
      cy.get("tbody > :nth-child(1) > :nth-child(5)").should("be.empty");
    });
  });
});
