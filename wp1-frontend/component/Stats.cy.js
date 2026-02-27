import { mount } from '@cypress/vue'
import Stats from '../../src/components/Stats.vue' 

describe('Stats Component', () => {
  it('renders', () => {
    mount(Stats)
    cy.get('div').should('exist') 
  })
})
