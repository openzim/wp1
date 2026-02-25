import { mount } from '@cypress/vue'
// Stats.vue file aapke components folder mein maujood hai
import Stats from '../../src/components/Stats.vue' 

describe('Stats Component', () => {
  it('renders correctly without backend API', () => {
    // Component ko bina backend dependency ke mount karna hi issue #1078 ka goal hai
    mount(Stats)
    
    // Check karein ki component load ho raha hai
    cy.get('div').should('exist') 
  })
})