//Tests adding people to the people page
describe('Getting to the people page', function (){
    it('Given: logs in successfully', function () {
        cy.visit('/login');
        cy.get('[data-cy=username]').type('Cytest');
        cy.get('[data-cy=password]').type('password');
        cy.get('[data-cy=login]').click();
        cy.url().should('include', '/admin');
    });
    it('When: people tab is pressed', function(){
        cy.get('.v-btn__content > .v-icon').click()
        cy.get('[data-cy=people]').click()
    });
    it('Then: url should have /people', function (){
        cy.url().should('include', '/people');
    });
}); 

//Fills in form then clears it
var testNum = 0;

describe('Fills out form then clears it', function (){
    it('Given: gets to add people form', function(){
        cy.get('[data-cy=new-person]').click()
    });
    it('When: form is filled out', function(){
        cy.get('[data-cy=firstName]').type('Test')//first name
        cy.get('[data-cy=lastName]').type(testNum)//last name
        cy.get(':nth-child(1) > .v-input--selection-controls__input > .v-input--selection-controls__ripple').click()//gender
        cy.get('.v-menu__activator > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot > input').click()//birthday options
        cy.get(':nth-child(3) > :nth-child(5) > .v-btn > .v-btn__content').click()//select birthday
        cy.get('[data-cy=email]').type('test'+ testNum + '@gmail.com')//email
        cy.get('[data-cy=phone]').type('123-456-7890')//phone
    });
    it('Then: check to see it saved or not', function(){
        cy.get('[data-cy=clear]').click()
        cy.get('[data-cy=firstName]').should('be.empty')
    });
});
