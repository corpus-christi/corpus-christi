import { unique_name, unique_email, unique_phone } from '../../support/helpers';

let first = unique_name();
let last = unique_name();
let email = unique_email();
let phone = unique_phone();

// This is how to target the bottommost bar in the form
//    form > :nth-child(2) > [style=""]

//Tests adding people to the people page

describe("Ensures the Add-person works", function() {
  before(() => {
    cy.login();
  });
  it("Given: logs in, navigates to people page", function() {
    cy.visit("/people");
  });

  it("When: The add button is pressed, form filled out, and submitted", () => {
    cy.get("[data-cy=new-person]").click();
    cy.get("[data-cy=first-name]").type(first); //first name
    cy.get("[data-cy=last-name]").type(last); //last name
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
    cy.get(".v-date-picker-header > :nth-child(1)").click();
    cy.get(".tab-reverse-transition-enter-active > tbody > :nth-child(2) > :nth-child(4) > .v-btn").click();
    
    // cy.get(":nth-child(3) > :nth-child(5) > .v-btn > .v-btn__content").click(); //select birthday
    cy.get("[data-cy=email]").type(email); //email
    cy.get("[data-cy=phone]").type(phone); //phone
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
    cy.get("[data-cy=search]").type(first);
    //goes through the info to ensure it is correct
    cy.get("[data-cy=person-table").within(() => {
      cy.get("tbody > :nth-child(1) > :nth-child(2)").should(
        "contain",
        first
      );
      cy.get("tbody > :nth-child(1) > :nth-child(3)").should("contain", last);
      cy.get("tbody > :nth-child(1) > :nth-child(4)").should(
        "contain",
        email
      );
      cy.get("tbody > :nth-child(1) > :nth-child(5)").should(
        "contain",
        phone
      );
    });
  });
});
