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

import com.josdem.vetlog.binder.PetLogBinder
import com.josdem.vetlog.command.PetLogCommand
import com.josdem.vetlog.exception.BusinessException
import com.josdem.vetlog.model.Pet
import com.josdem.vetlog.model.PetLog
import com.josdem.vetlog.repository.PetLogRepository
import com.josdem.vetlog.repository.PetRepository
import com.josdem.vetlog.service.impl.PetLogServiceImpl
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.assertThrows
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.slf4j.LoggerFactory
import java.io.IOException
import kotlin.test.Test
import java.util.Optional

internal class PetLogServiceTest {

    private lateinit var service: PetLogService

    private val pet = Pet()

    @Mock
    private lateinit var petLogBinder: PetLogBinder

    @Mock
    private lateinit var petLogRepository: PetLogRepository

    @Mock
    private lateinit var petRepository: PetRepository

    @Mock
    private lateinit var petPrescriptionService: PetPrescriptionService

    companion object {
        private val log = LoggerFactory.getLogger(PetLogServiceTest::class.java)
    }

    @BeforeEach
    fun setup() {
        MockitoAnnotations.openMocks(this)
        service = PetLogServiceImpl(petLogBinder, petLogRepository, petRepository, petPrescriptionService)
    }

    @Test
    @Throws(IOException::class)
    fun `Saving a pet log`() {
        log.info("Running test: Saving a pet log")
        val petLogCommand = PetLogCommand().apply { pet = 1L }
        val petLog = getPetLog()
        val optionalPet: Optional<Pet> = Optional.ofNullable(pet)

        whenever(petLogBinder.bind(petLogCommand)).thenReturn(petLog)
        whenever(petRepository.findById(1L)).thenReturn(optionalPet)

        service.save(petLogCommand)
        verify(petLogRepository).save(petLog)
    }

    @Test
    fun `Should not find a pet log`() {
        log.info("Running test: Should not find a pet log")
        val petLogCommand = PetLogCommand()
        val petLog = getPetLog()

        whenever(petLogBinder.bind(petLogCommand)).thenReturn(petLog)

        assertThrows<BusinessException> {
            service.save(petLogCommand)
        }
    }

    @Test
    fun `Getting logs by pet`() {
        log.info("Running test: Getting logs by pet")
        val petLog = getPetLog()
        whenever(petLogRepository.getAllByPet(pet)).thenReturn(mutableListOf(petLog))

        val result = service.getPetLogsByPet(pet)

        Assertions.assertEquals(listOf(petLog), result)
    }

    private fun getPetLog(): PetLog {
        return PetLog().apply { pet = this@PetLogServiceTest.pet }
    }
}

