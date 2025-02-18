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

import static org.mockito.Mockito.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.josdem.vetlog.command.UserCommand;
import com.josdem.vetlog.model.User;
import com.josdem.vetlog.repository.UserRepository;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.validation.Errors;

@Slf4j
class UserValidatorTest {

    private UserValidator validator;
    private Errors errors = mock(Errors.class);

    @Mock
    private UserRepository userRepository;

    @BeforeEach
    void setup() {
        MockitoAnnotations.openMocks(this);
        validator = new UserValidator(userRepository);
    }

    @Test
    @DisplayName("validating an user")
    void shouldValidateAnUser(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        var userCommand = getUserCommand();
        validator.validate(userCommand, errors);
        verify(errors, never()).rejectValue(anyString(), anyString());
    }

    @Test
    @DisplayName("rejecting an user since passwords do not match")
    void shouldRejectUserSincePasswordDoesNotMatch(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        var userCommand = getUserCommand();
        userCommand.setPasswordConfirmation("passwords");
        validator.validate(userCommand, errors);
        verify(errors).rejectValue("password", "user.error.password.equals");
    }

    @DisplayName("accepting passwords")
    @ParameterizedTest
    @ValueSource(strings = {"pass-word", "pass_word", "password."})
    void shouldAcceptDashCharacterInPassword(String password) {
        log.info("Running: accepting passwords");
        var userCommand = getUserCommand();
        userCommand.setPassword(password);
        userCommand.setPasswordConfirmation(password);
        validator.validate(userCommand, errors);
        verify(errors, never()).rejectValue(anyString(), anyString());
    }

    @Test
    @DisplayName("accepting underscore in password")
    void shouldAcceptUnderscoreCharacterInPassword(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        var userCommand = getUserCommand();
        userCommand.setPassword("pass_word");
        userCommand.setPasswordConfirmation("pass_word");
        validator.validate(userCommand, errors);
        verify(errors, never()).rejectValue(anyString(), anyString());
    }

    @Test
    @DisplayName("accepting dot in password")
    void shouldAcceptDotCharacterInPassword(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        var userCommand = getUserCommand();
        userCommand.setPassword("password.");
        userCommand.setPasswordConfirmation("password.");
        validator.validate(userCommand, errors);
        verify(errors, never()).rejectValue(anyString(), anyString());
    }

    @Test
    @DisplayName("not duplicating users")
    void shouldNotDuplicateUsers(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        var userCommand = getUserCommand();
        when(userRepository.findByUsername("josdem")).thenReturn(Optional.of(new User()));
        validator.validate(userCommand, errors);
        verify(errors).rejectValue("username", "user.error.duplicated.username");
    }

    @Test
    @DisplayName("not duplicating users by email")
    void shouldNotDuplicateUsersByEmail(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        var userCommand = getUserCommand();
        when(userRepository.findByEmail("contact@josdem.io")).thenReturn(Optional.of(new User()));
        validator.validate(userCommand, errors);
        verify(errors).rejectValue("email", "user.error.duplicated.email");
    }

    @Test
    @DisplayName("rejecting an user since mobile format is not valid")
    void shouldRejectUserSinceInvalidMobile(TestInfo testInfo) {
        log.info("Running: {}", testInfo.getDisplayName());
        var userCommand = getUserCommand();
        userCommand.setMobile("notValidPhoneNumber");
        validator.validate(userCommand, errors);
        verify(errors).rejectValue("mobile", "user.error.mobile");
    }

    private UserCommand getUserCommand() {
        var userCommand = new UserCommand();
        userCommand.setUsername("josdem");
        userCommand.setPassword("password");
        userCommand.setPasswordConfirmation("password");
        userCommand.setFirstname("Jose");
        userCommand.setLastname("Morales");
        userCommand.setEmail("contact@josdem.io");
        userCommand.setMobile("1234567890");
        return userCommand;
    }
}
