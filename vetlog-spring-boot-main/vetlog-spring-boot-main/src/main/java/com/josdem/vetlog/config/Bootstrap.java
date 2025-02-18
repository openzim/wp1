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

package com.josdem.vetlog.config;

import com.josdem.vetlog.enums.CurrentEnvironment;
import com.josdem.vetlog.enums.Role;
import com.josdem.vetlog.model.User;
import com.josdem.vetlog.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.ApplicationListener;
import org.springframework.core.env.Environment;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class Bootstrap implements ApplicationListener<ApplicationReadyEvent> {

    private final Environment environment;
    private final UserRepository userRepository;

    private static final String SECRET = "12345678";

    @Override
    public void onApplicationEvent(final ApplicationReadyEvent event) {
        if (environment.getActiveProfiles()[0].equals(CurrentEnvironment.DEVELOPMENT.getDescription())) {
            log.info("Loading development environment");
            createDefaultUsers();
        }
    }

    void createDefaultUsers() {
        createUserWithRole("josdem", "joseluis.delacruz@gmail.com", "1234567890", Role.USER);
        createUserWithRole("miriam", "miriam@gmail.com", "1112223334", Role.USER);
        createUserWithRole("admin", "admin@email.com", "5556667778", Role.ADMIN);
    }

    void createUserWithRole(String username, String email, String mobile, Role authority) {
        if (userRepository.findByUsername(username).isEmpty()) {
            log.info("Creating user: {}", username);
            User user = new User();
            user.setUsername(username);
            user.setPassword(new BCryptPasswordEncoder().encode(SECRET));
            user.setEmail(email);
            user.setRole(authority);
            user.setFirstName(username);
            user.setLastName(username);
            user.setMobile(mobile);
            user.setEnabled(true);
            userRepository.save(user);
        }
    }
}
