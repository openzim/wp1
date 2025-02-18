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

import com.josdem.vetlog.command.AdoptionCommand
import com.josdem.vetlog.enums.PetStatus
import com.josdem.vetlog.model.Pet
import com.josdem.vetlog.repository.PetRepository
import com.josdem.vetlog.service.impl.AdoptionServiceImpl
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever
import org.mockito.kotlin.verify
import org.slf4j.LoggerFactory
import kotlin.test.Test

internal class AdoptionServiceTest {

    private lateinit var service: AdoptionService

    @Mock
    private lateinit var petService: PetService

    @Mock
    private lateinit var petRepository: PetRepository

    companion object {
        private val log = LoggerFactory.getLogger(AdoptionServiceTest::class.java)
    }

    @BeforeEach
    fun setup() {
        MockitoAnnotations.openMocks(this)
        service = AdoptionServiceImpl(petService, petRepository)
    }

    @Test
    fun `Saving a pet in adoption`() {
        log.info("Running test: saving a pet in adoption")
        val adoptionCommand = getAdoptionCommand()
        val pet = getPet()

        whenever(petService.getPetByUuid("uuid")).thenReturn(pet)
        val result = service.save(adoptionCommand)

        verify(petRepository).save(pet)
        Assertions.assertEquals(PetStatus.IN_ADOPTION, pet.status)
        Assertions.assertEquals(pet, result.pet)
        Assertions.assertEquals("description", result.description)
    }

    private fun getPet(): Pet {
        return Pet().apply {
            status = PetStatus.OWNED
        }
    }

    private fun getAdoptionCommand(): AdoptionCommand {
        return AdoptionCommand().apply {
            uuid = "uuid"
            description = "description"
        }
    }
}
