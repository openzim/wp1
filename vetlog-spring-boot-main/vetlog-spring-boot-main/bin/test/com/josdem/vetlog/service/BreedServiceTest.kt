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

import com.josdem.vetlog.model.Breed
import com.josdem.vetlog.repository.BreedRepository
import com.josdem.vetlog.service.impl.BreedServiceImpl
import com.josdem.vetlog.enums.PetType
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.TestInfo
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever
import org.mockito.kotlin.verify
import org.slf4j.LoggerFactory
import kotlin.test.Test

internal class BreedServiceTest {

    private lateinit var service: BreedService

    @Mock
    private lateinit var breedRepository: BreedRepository

    companion object {
        private val log = LoggerFactory.getLogger(BreedServiceTest::class.java)
    }

    @BeforeEach
    fun setup() {
        MockitoAnnotations.openMocks(this)
        service = BreedServiceImpl(breedRepository)
    }

    @Test
    fun `Getting breeds by type`() {
        log.info("Running test: getting breeds by type")

        val mockBreeds = listOf(Breed()) // Kotlin の listOf を使用
        whenever(breedRepository.findByType(PetType.DOG)).thenReturn(mockBreeds)

        val breeds = service.getBreedsByType(PetType.DOG)

        Assertions.assertTrue(breeds.isNotEmpty(), "should have a breed")
        verify(breedRepository).findByType(PetType.DOG)
    }
}
