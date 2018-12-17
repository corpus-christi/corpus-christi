describe('Locale Selector', function () {
    it('contains test locales', function () {
        cy.visit('/locale');
        cy.contains('Locales');
    })
});