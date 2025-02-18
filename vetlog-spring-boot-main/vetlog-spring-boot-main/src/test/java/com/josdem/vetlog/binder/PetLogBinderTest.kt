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

package com.josdem.vetlog.binder

import com.josdem.vetlog.command.PetLogCommand
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInfo
import org.slf4j.LoggerFactory

internal class PetLogBinderTest {

    val petLogBinder = PetLogBinder()

    companion object {
        private val log = LoggerFactory.getLogger(PetLogBinderTest::class.java)
    }

    @Test
    fun `binding a pet log command`(testInfo: TestInfo) {
        log.info(testInfo.displayName)

        val petLogCommand = PetLogCommand().apply {
            vetName = "Diana Juarez"
            signs = "Cough"
            diagnosis = "Bronchitis"
            medicine = "Antibiotics"
        }

        val result = petLogBinder.bind(petLogCommand)

        assertEquals("Diana Juarez", result.vetName);
        assertEquals("Cough", result.signs);
        assertEquals("Bronchitis", result.diagnosis);
        assertEquals("Antibiotics", result.medicine);
    }

}