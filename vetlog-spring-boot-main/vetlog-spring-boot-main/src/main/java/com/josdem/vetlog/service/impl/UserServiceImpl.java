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

import com.josdem.vetlog.binder.UserBinder;
import com.josdem.vetlog.command.Command;
import com.josdem.vetlog.config.ApplicationProperties;
import com.josdem.vetlog.exception.UserNotFoundException;
import com.josdem.vetlog.model.User;
import com.josdem.vetlog.repository.UserRepository;
import com.josdem.vetlog.service.EmailService;
import com.josdem.vetlog.service.UserService;
import com.josdem.vetlog.util.UserContextHolderProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@EnableConfigurationProperties(ApplicationProperties.class)
public class UserServiceImpl implements UserService {

    public static final String NOT_FOUND = " not found";

    private final UserBinder userBinder;
    private final UserRepository userRepository;
    private final UserContextHolderProvider provider;
    private final ApplicationProperties applicationProperties;
    private final EmailService emailService;

    public User getByUsername(String username) {
        return userRepository
                .findByUsername(username)
                .or(() -> userRepository.findByMobile(username))
                .orElseThrow(() -> new UserNotFoundException("User " + NOT_FOUND));
    }

    public User getByEmail(String email) {
        return userRepository
                .findByEmail(email)
                .orElseThrow(() -> new UserNotFoundException("User with email: " + email + NOT_FOUND));
    }

    @Override
    public User getByMobile(String mobile) {
        return userRepository
                .findByMobile(mobile)
                .orElseThrow(() -> new UserNotFoundException("User with mobile: " + mobile + NOT_FOUND));
    }

    @Transactional
    public User save(Command command) {
        var user = userBinder.bindUser(command);
        if (applicationProperties.getCountryCodes().contains(user.getCountryCode())) {
            user.setEnabled(false);
        }
        emailService.sendWelcomeEmail(user);
        userRepository.save(user);
        return user;
    }

    public User getCurrentUser() {
        var auth = provider.getAuthentication();
        var username = auth.getName();
        return userRepository
                .findByUsername(username)
                .orElseThrow(() -> new UserNotFoundException("User with username: " + username + NOT_FOUND));
    }
}
