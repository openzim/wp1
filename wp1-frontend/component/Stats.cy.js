import { mount } from '@cypress/vue'
import Stats from '../../src/components/Stats.vue' 

describe('Stats Component', () => {
  it('renders correctly without backend API', () => {
   
    mount(Stats)
    cy.get('div').should('exist') 
  })
})
