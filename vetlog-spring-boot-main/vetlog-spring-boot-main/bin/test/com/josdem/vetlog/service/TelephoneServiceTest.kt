/*
  Copyright 2025 Jose Morales contact@josdem.io

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/
package com.josdem.vetlog.service

import com.josdem.vetlog.command.MessageCommand
import com.josdem.vetlog.command.TelephoneCommand
import com.josdem.vetlog.enums.PetStatus
import com.josdem.vetlog.model.Pet
import com.josdem.vetlog.model.User
import com.josdem.vetlog.repository.PetRepository
import com.josdem.vetlog.repository.UserRepository
import com.josdem.vetlog.service.impl.TelephoneServiceImpl
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.mockito.kotlin.any
import org.slf4j.LoggerFactory
import java.io.IOException
import kotlin.test.Test

internal class TelephoneServiceTest {
    private lateinit var service: TelephoneService

    @Mock
    private lateinit var petService: PetService

    @Mock
    private lateinit var restService: RestService

    @Mock
    private lateinit var userRepository: UserRepository

    @Mock
    private lateinit var petRepository: PetRepository

    companion object {
        private val log = LoggerFactory.getLogger(TelephoneServiceTest::class.java)
    }

    @BeforeEach
    fun setup() {
        MockitoAnnotations.openMocks(this)
        service = TelephoneServiceImpl(petService, restService, userRepository, petRepository)
    }

    @Test
    @Throws(IOException::class)
    fun `Sending adopter contact information to the pet owner`() {
        log.info("Running test: Sending adopter contact information to the pet owner")
        val telephoneCommand = TelephoneCommand().apply {
            uuid = "uuid"
            mobile = "7346041832"
        }

        val owner = getUser("contact@josdem.io")
        val adopter = getUser("athena@gmail.com")
        val pet = getPet(owner, adopter)

        whenever(petService.getPetByUuid("uuid")).thenReturn(pet)
        service.save(telephoneCommand, adopter)

        verify(petRepository).save(pet)
        verify(userRepository).save(adopter)
        verify(restService).sendMessage(any<MessageCommand>())
        Assertions.assertEquals(PetStatus.ADOPTED, pet.status)
        Assertions.assertEquals(adopter, pet.adopter)
    }

    private fun getPet(owner: User?, adopter: User?): Pet {
        return Pet().apply {
            name = "Cinnamon"
            this.user = owner
            this.adopter = adopter
        }
    }

    private fun getUser(email: String?): User {
        return User().apply {
            this.email = email
        }
    }
}
