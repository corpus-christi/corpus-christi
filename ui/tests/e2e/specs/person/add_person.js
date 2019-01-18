//Tests adding people to the people page
describe("Ensures the Add-person works", function() {
  it("Given: logs in, navigates to people page", function () {
    cy.login();
    cy.get('[data-cy=toggle-nav-drawer]').click();
    cy.get("[data-cy=people]").click();
    cy.url().should("include", "/people");
  });
  it("When: The add button is pressed, form filled out, and submitted", () => {
    cy.get("[data-cy=new-person]").click();
    cy.get("[data-cy=first-name]").type("Pepsi"); //first name
    cy.get("[data-cy=last-name]").type("Cola"); //last name
    cy.get("[data-cy=radio-gender]").within(() => {//Enters the gender radio button field
      cy.get(".v-label").last().click();//Female
      cy.get(".v-label").first().click();//Male
    });
    cy.get("[data-cy=show-birthday-picker]").click(); //open birthday picker
    cy.get(":nth-child(3) > :nth-child(5) > .v-btn > .v-btn__content").click(); //select birthday
    cy.get("[data-cy=email]").type("SoftDrink@gmail.com"); //email
    cy.get("[data-cy=phone]").type("123-456-7890"); //phone
    cy.get('[data-cy = save]').click();
  });
  it("Then: The user should show up in the database with the correct information", () => {
    cy.get('[data-cy=search]').type("Pepsi");
    //goes through the info to ensure it is correct
    cy.get('tbody > :nth-child(1) > :nth-child(2)').should('contain', 'Pepsi');
    cy.get('tbody > :nth-child(1) > :nth-child(3)').should('contain', 'Cola');
    cy.get('tbody > :nth-child(1) > :nth-child(4)').should('contain', 'SoftDrink@gmail.com');
    cy.get('tbody > :nth-child(1) > :nth-child(5)').should('contain', '123-456-7890');
  });
});
describe("Tests the add-person form to ensure proper functionality", () => {
  it("Ensure form fields work as they should", () => {
    cy.get("[data-cy=new-person]").click();
    //Making sure that name fields do not allow numbers
        //waiting on this to actually be implemented by UI
    //Making sure that the phone field does not allow letters & has a length limit
        //waiting on this to actually be implemented by UI
    //Make sure you cannot select a date in the future
        //waiting on this to actually be implemented by UI
      //cy.get('.v-date-picker-header > :nth-child(3)').click();
      //cy.contains('17').click();
    //Make sure the email is valid
    cy.get('[data-cy=email]').type("NotARealEmail");
    cy.get('[data-cy=save]').click();
    cy.get(':nth-child(6) > .v-input__control > .v-text-field__details').contains("válido");
    cy.get('[data-cy=email]').clear().type("testEmail@aol.com");
    cy.get('[data-cy=save]').click();
    cy.get(':nth-child(6) > .v-input__control > .v-text-field__details').should('not.contain',"válido");


  });

  it("Clear button works correctly", () => {
    cy.get("[data-cy=first-name]").type("Test"); //first name
    cy.get("[data-cy=last-name]").type("Me"); //last name
    cy.get("[data-cy=radio-gender]").within(() => {
      cy.get(".v-label").first().click();
    });
    cy.get("[data-cy=show-birthday-picker]").click(); //open birthday picker
    cy.get(":nth-child(3) > :nth-child(5) > .v-btn > .v-btn__content").click(); //select birthday
    cy.get("[data-cy=phone]").type("123-456-7890"); //phone
    cy.get("[data-cy=clear]").click();
    cy.get("[data-cy=first-name]").should("be.empty");
    cy.get('[data-cy=last-name]').should("be.empty");
    cy.get('[data-cy=phone]').should("be.empty");
    cy.get('[data-cy=email]').should("be.empty");
  });
  it("Ensure the form is filled out with enough information before save/add another can proceed", () => {
    cy.get('[data-cy = save]').click();
    cy.get(':nth-child(1) > .v-input__control > .v-text-field__details').contains("obligatorio");
    cy.get(':nth-child(2) > .v-input__control > .v-text-field__details').contains("obligatorio");
    cy.get("[data-cy=first-name]").type("Test"); //first name
    cy.get("[data-cy=last-name]").type("Me"); //last name
    cy.get('[data-cy=add-another]').click();
    cy.get("[data-cy=first-name]").should("be.empty");
    cy.get('[data-cy=last-name]').should("be.empty");
  });
  it("The exit form button works correctly", () => {
    cy.get('[data-cy=cancel').click();
    cy.get('.v-dialog__content--active > .v-dialog').should('not.exist');
  });


});
