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

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;

import com.josdem.vetlog.command.PetCommand;
import lombok.extern.slf4j.Slf4j;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.springframework.validation.Errors;

@Slf4j
class PetValidatorTest {

    private final PetValidator validator = new PetValidator();
    private final Errors errors = mock(Errors.class);

    @Test
    @DisplayName("validating birthdate")
    void shouldValidateBirthdate(TestInfo testInfo) {
        log.info(testInfo.getDisplayName());
        var petCommand = getPetCommand("2021-01-17");
        validator.validate(petCommand, errors);
        verify(errors, never()).rejectValue(anyString(), anyString());
    }

    @Test
    @DisplayName("validating empty birthdate")
    void shouldValidateEmptyBirthdate(TestInfo testInfo) {
        log.info(testInfo.getDisplayName());
        var petCommand = getPetCommand("");
        validator.validate(petCommand, errors);
        verify(errors, never()).rejectValue(anyString(), anyString());
    }

    @Test
    @DisplayName("rejecting a birthdate")
    void shouldRejectBirthdate(TestInfo testInfo) {
        log.info(testInfo.getDisplayName());
        var petCommand = getPetCommand("2026-01-17");
        validator.validate(petCommand, errors);
        verify(errors).rejectValue("birthDate", "pet.error.birthDate.past");
    }

    @NotNull
    private PetCommand getPetCommand(String birthdate) {
        var petCommand = new PetCommand();
        petCommand.setBirthDate(birthdate);
        return petCommand;
    }
}
