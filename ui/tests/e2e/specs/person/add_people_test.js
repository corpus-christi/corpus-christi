//Tests adding people to the people page
describe("Getting to the people page", function() {
  it("Given: logs in successfully", function() {
    cy.visit("/login");
    cy.get("[data-cy=username]").type("Cytest");
    cy.get("[data-cy=password]").type("password");
    cy.get("[data-cy=login]").click();
    cy.url().should("include", "/admin");
  });
  it("When: people tab is pressed", function() {
    cy.get(".v-btn__content > .v-icon").click();
    cy.get("[data-cy=people]").click();
  });
  it("Then: url should have /people", function() {
    cy.url().should("include", "/people");
  });
});

//Adds people
//NEED TO INCREASE testNum SO THAT THERE IS NO DUPLICATION OF PEOPLE
var testNum = 12;
testNum = testNum + 1;
describe("Filling out form", function() {
  it("Given: gets to add people form", function() {
    cy.get("[data-cy=new-person]").click();
  });
  it("When: form is filled out", function() {
    cy.get("[data-cy=first-name]").type("Test"); //first name
    cy.get("[data-cy=last-name]").type(testNum); //last name
    cy.get("[data-cy=radio-gender]").click(); //gender
    cy.get("[data-cy=show-birthday-picker]").click(); //open birthday picker
    cy.get(":nth-child(3) > :nth-child(5) > .v-btn > .v-btn__content").click(); //select birthday
    cy.get("[data-cy=email]").type("test" + testNum + "@gmail.com"); //email
    cy.get("[data-cy=phone]").type("123-456-7890"); //phone
  });
  it("Then: check to see it saved or not", function() {
    cy.get("[data-cy=save]").click();
    cy.get("[data-cy=search]").type("Test");
    cy.get(
      ".v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(".v-select-list > .v-list > :nth-child(4) > .v-list__tile").click();
    cy.get(".container").contains(testNum);
  });
});
