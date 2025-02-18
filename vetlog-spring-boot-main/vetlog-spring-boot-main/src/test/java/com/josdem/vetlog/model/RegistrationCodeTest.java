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

package com.josdem.vetlog.model;

import static java.time.temporal.ChronoUnit.DAYS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.josdem.vetlog.enums.RegistrationCodeStatus;
import java.time.LocalDateTime;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;

@Slf4j
class RegistrationCodeTest {

    private RegistrationCode registrationCode = new RegistrationCode();

    @Test
    @DisplayName("getting a valid registration code")
    void shouldGetValidRegistrationCode(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        assertEquals(
                7,
                DAYS.between(
                        registrationCode.getDateCreated(), LocalDateTime.now().plusDays(7)));
        assertEquals(36, registrationCode.getToken().length());
        assertTrue(registrationCode.isValid());
    }

    @Test
    @DisplayName("invalidating a token")
    void shouldInvalidateToken(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        registrationCode.setStatus(RegistrationCodeStatus.INVALID);
        assertFalse(registrationCode.isValid());
    }
}
