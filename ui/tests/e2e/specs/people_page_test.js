//Tests logging in and going to the people page
describe('Clicking home after logging in', function (){
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