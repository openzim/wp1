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

package com.josdem.vetlog.service.impl;

import com.josdem.vetlog.command.ChangePasswordCommand;
import com.josdem.vetlog.command.Command;
import com.josdem.vetlog.command.MessageCommand;
import com.josdem.vetlog.exception.BusinessException;
import com.josdem.vetlog.exception.UserNotFoundException;
import com.josdem.vetlog.exception.VetlogException;
import com.josdem.vetlog.model.User;
import com.josdem.vetlog.repository.RegistrationCodeRepository;
import com.josdem.vetlog.repository.UserRepository;
import com.josdem.vetlog.service.LocaleService;
import com.josdem.vetlog.service.RecoveryService;
import com.josdem.vetlog.service.RegistrationService;
import com.josdem.vetlog.service.RestService;
import java.io.IOException;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class RecoveryServiceImpl implements RecoveryService {

    public static final String USER_NOT_FOUND = "user.not.found";

    private final RestService restService;
    private final RegistrationService registrationService;
    private final UserRepository userRepository;
    private final RegistrationCodeRepository repository;
    private final LocaleService localeService;

    @Value("${baseUrl}")
    private String baseUrl;

    @Value("${token}")
    private String clientToken;

    @Value("${template.forgot.name}")
    private String forgotTemplate;

    @Value("${template.forgot.path}")
    private String forgotPath;

    public User confirmAccountForToken(String token) {
        var user = getUserByToken(token);
        user.setEnabled(true);
        userRepository.save(user);
        return user;
    }

    public User getUserByToken(String token) {
        var email = registrationService
                .findEmailByToken(token)
                .orElseThrow(() -> new VetlogException(localeService.getMessage("exception.token.not.found")));
        return userRepository
                .findByEmail(email)
                .orElseThrow(() -> new UserNotFoundException(localeService.getMessage(USER_NOT_FOUND)));
    }

    public void generateRegistrationCodeForEmail(String email) {
        var user = userRepository
                .findByEmail(email)
                .orElseThrow(() -> new UserNotFoundException(localeService.getMessage(USER_NOT_FOUND)));
        if (!user.isEnabled()) {
            throw new VetlogException(localeService.getMessage("exception.account.not.activated"));
        }
        try {
            var token = registrationService.generateToken(email);
            var command = new MessageCommand();
            command.setEmail(email);
            command.setName(email);
            command.setTemplate(forgotTemplate);
            command.setMessage(baseUrl + forgotPath + token);
            command.setToken(clientToken);
            restService.sendMessage(command);
        } catch (IOException ioException) {
            throw new BusinessException(ioException.getMessage());
        }
    }

    public Boolean validateToken(String token) {
        return repository.findByToken(token).isPresent();
    }

    public User changePassword(Command command) {
        var changePasswordCommand = (ChangePasswordCommand) command;
        var user = getUserByToken(changePasswordCommand.getToken());
        user.setPassword(new BCryptPasswordEncoder().encode(changePasswordCommand.getPassword()));
        userRepository.save(user);
        return user;
    }
}
