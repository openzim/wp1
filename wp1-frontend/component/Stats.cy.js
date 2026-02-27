import { mount } from '@cypress/vue'
<<<<<<< HEAD

=======
>>>>>>> f6a5520569b196b62d58f2632a042ede6a960ad3
import Stats from '../../src/components/Stats.vue' 

describe('Stats Component', () => {
  it('renders correctly without backend API', () => {
<<<<<<< HEAD
=======
   
>>>>>>> f6a5520569b196b62d58f2632a042ede6a960ad3
    mount(Stats)
    cy.get('div').should('exist') 
  })
})
