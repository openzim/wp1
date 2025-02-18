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
import static org.mockito.Mockito.verify;

import com.josdem.vetlog.command.ChangePasswordCommand;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.springframework.validation.Errors;

@Slf4j
class ChangePasswordValidatorTest {

    private ChangePasswordValidator validator = new ChangePasswordValidator();

    @Test
    @DisplayName("not validating since password does not match")
    void shouldRejectSincePasswordsAreNotEquals(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        var command = new ChangePasswordCommand();
        command.setToken("token");
        command.setPassword("password");
        command.setPasswordConfirmation("passwords");
        var errors = mock(Errors.class);
        validator.validate(command, errors);
        verify(errors).rejectValue("password", "user.error.password.equals");
    }
}
