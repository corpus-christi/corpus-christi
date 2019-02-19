// This is how to target the bottommost bar in the form
//    form > :nth-child(2) > [style=""]

//Tests adding people to the people page

describe("Ensures the Add-person works", function() {
  it("Given: logs in, navigates to people page", function() {
    cy.login();
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=people]").click();
    cy.url().should("include", "/people");
  });

  it("When: The add button is pressed, form filled out, and submitted", () => {
    cy.get("[data-cy=new-person]").click();
    cy.get("[data-cy=first-name]").type("Pepsi"); //first name
    cy.get("[data-cy=last-name]").type("Cola"); //last name
    cy.get("[data-cy=radio-gender]").within(() => {
      //Enters the gender radio button field
      cy.get(".v-label")
        .last()
        .click(); //Female
      cy.get(".v-label")
        .first()
        .click(); //Male
    });
    cy.get("[data-cy=show-birthday-picker]").click(); //open birthday picker
    cy.get(":nth-child(3) > :nth-child(5) > .v-btn > .v-btn__content").click(); //select birthday
    cy.get("[data-cy=email]").type("SoftDrink@gmail.com"); //email
    cy.get("[data-cy=phone]").type("123-456-7890"); //phone
    //This is where the test diverges
    cy.get('form > :nth-child(2) > [style=""]').within(() => {
      cy.get("[data-cy=next]").click();
    });
    //cy.scrollTo(0, 50);
    cy.get('[style=""] > .v-stepper__wrapper > .layout').within(() => {
      cy.get("[data-cy=next]")
        .eq(1)
        .click();
    });
    cy.get('form > :nth-child(2) > [style=""]').within(() => {
      cy.get("[data-cy=save]").click();
    });
  });
  it("Then: The user should show up in the database with the correct information", () => {
    cy.get("[data-cy=search]").type("Pepsi");
    //goes through the info to ensure it is correct
    cy.get("[data-cy=person-table").within(() => {
      cy.get("tbody > :nth-child(1) > :nth-child(2)").should(
        "contain",
        "Pepsi"
      );
      cy.get("tbody > :nth-child(1) > :nth-child(3)").should("contain", "Cola");
      cy.get("tbody > :nth-child(1) > :nth-child(4)").should(
        "contain",
        "SoftDrink@gmail.com"
      );
      cy.get("tbody > :nth-child(1) > :nth-child(5)").should(
        "contain",
        "123-456-7890"
      );
    });
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
    cy.get("[data-cy=email]").type("NotARealEmail");
    //cy.get("[data-cy=save]").click();
    cy.get("[data-cy=first-name]").click();
    cy.get(
      ":nth-child(6) > .v-input__control > .v-text-field__details"
    ).contains("válido");
    cy.get("[data-cy=email]")
      .clear()
      .type("testEmail@gmail.com");
    cy.get("[data-cy=first-name]").click();
    cy.get(":nth-child(6) > .v-input__control > .v-text-field__details").should(
      "not.contain",
      "válido"
    );

    cy.get('form > :nth-child(2) > [style=""]').within(() => {
      cy.get("[data-cy=next]").click();
    });
    //cy.scrollTo(0, 50);
    cy.get('[style=""] > .v-stepper__wrapper > .layout').within(() => {
      cy.get("[data-cy=next]")
        .eq(1)
        .click();
    });
    cy.get('form > :nth-child(2) > [style=""]').within(() => {
      cy.get("[data-cy=save]").click();
    });
    cy.get(
      ":nth-child(1) > .v-input__control > .v-text-field__details"
    ).contains("obligatorio");
    cy.get(
      ":nth-child(2) > .v-input__control > .v-text-field__details"
    ).contains("obligatorio");
    cy.get("[data-cy=first-name]").type("Test"); //first name
    cy.get("[data-cy=last-name]").type("Me"); //last name
    cy.get(
      '[style=""] > .v-stepper__wrapper > :nth-child(1) > .v-input__control > .v-text-field__details > .v-messages'
    ).should("not.contain", "obligatorio");
    cy.get(
      '[style=""] > .v-stepper__wrapper > :nth-child(2) > .v-input__control > .v-text-field__details > .v-messages'
    ).should("not.contain", "obligatorio");
  });
  it("Finally: Fields should be valid before add another is allowed to work & after pressed, fields should be cleared", function() {
    cy.get('form > :nth-child(2) > [style=""]').within(() => {
      cy.get("[data-cy=next]").click();
    });
    //cy.scrollTo(0, 50);
    cy.get('[style=""] > .v-stepper__wrapper > .layout').within(() => {
      cy.get("[data-cy=next]")
        .eq(1)
        .click();
    });
    cy.get('form > :nth-child(2) > [style=""]').within(() => {
      cy.get("[data-cy=add-another]").click();
    });
    cy.get("[data-cy=first-name]").should("be.empty");
    cy.get("[data-cy=last-name]").should("be.empty");
    cy.get("[data-cy=phone]").should("be.empty");
    cy.get("[data-cy=email]").should("be.empty");

    cy.get("[data-cy=cancel")
      .first()
      .click();
    cy.get(".v-dialog__content--active > .v-dialog").should("not.exist");
  });
});
