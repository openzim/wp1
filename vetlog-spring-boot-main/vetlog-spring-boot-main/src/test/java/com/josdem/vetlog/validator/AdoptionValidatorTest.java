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

package com.josdem.vetlog.validator;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;

import com.josdem.vetlog.command.AdoptionCommand;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.springframework.validation.Errors;

@Slf4j
class AdoptionValidatorTest {

    private static final String UUID = "21740c48-13f9-4bf4-a8a2-ef61b7d3cdc3";
    private final AdoptionValidator adoptionValidator = new AdoptionValidator();

    @Test
    @DisplayName("rejecting adoption command with invalid uuid")
    void shouldRejectDueToInvalidUuid(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        var adoptionCommand = new AdoptionCommand();
        var errors = mock(Errors.class);
        adoptionCommand.setUuid("uuid");
        adoptionValidator.validate(adoptionCommand, errors);
        verify(errors).rejectValue("uuid", "adoption.error.uuid.invalid");
    }

    @Test
    @DisplayName("validating adoption command with valid uuid")
    void shouldValidateWithValidUuid(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        var adoptionCommand = new AdoptionCommand();
        var errors = mock(Errors.class);
        adoptionCommand.setUuid(UUID);
        adoptionValidator.validate(adoptionCommand, errors);
        verify(errors, never()).rejectValue("uuid", "adoption.error.uuid.invalid");
    }
}
