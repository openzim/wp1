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

import com.josdem.vetlog.command.UserCommand;
import com.josdem.vetlog.model.User;
import com.josdem.vetlog.repository.UserRepository;
import java.util.Optional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.validation.Errors;
import org.springframework.validation.Validator;

@Slf4j
@Component
@RequiredArgsConstructor
public class UserValidator implements Validator {

    private static final String NUMERIC_REGEX = "\\d+";

    private final UserRepository userRepository;

    @Override
    public boolean supports(Class<?> clazz) {
        return UserCommand.class.equals(clazz);
    }

    @Override
    public void validate(Object target, Errors errors) {
        UserCommand userCommand = (UserCommand) target;
        validatePasswords(errors, userCommand);
        validateUsername(errors, userCommand);
        validateMobile(errors, userCommand);
        validateEmail(errors, userCommand);
    }

    private void validateMobile(Errors errors, UserCommand command) {
        if (!command.getMobile().matches(NUMERIC_REGEX)) {
            errors.rejectValue("mobile", "user.error.mobile");
        }
    }

    private void validatePasswords(Errors errors, UserCommand command) {
        if (!command.getPassword().equals(command.getPasswordConfirmation())) {
            errors.rejectValue("password", "user.error.password.equals");
        }
    }

    private void validateUsername(Errors errors, UserCommand command) {
        Optional<User> optional = userRepository.findByUsername(command.getUsername());
        if (optional.isPresent()) {
            errors.rejectValue("username", "user.error.duplicated.username");
        }
    }

    public void validateEmail(Errors errors, UserCommand command) {
        Optional<User> optional = userRepository.findByEmail(command.getEmail());
        if (optional.isPresent()) {
            errors.rejectValue("email", "user.error.duplicated.email");
        }
    }
}
