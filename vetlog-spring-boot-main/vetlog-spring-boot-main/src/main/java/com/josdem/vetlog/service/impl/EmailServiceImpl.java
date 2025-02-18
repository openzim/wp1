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

import com.josdem.vetlog.command.MessageCommand;
import com.josdem.vetlog.config.TemplateProperties;
import com.josdem.vetlog.exception.BusinessException;
import com.josdem.vetlog.model.User;
import com.josdem.vetlog.service.EmailService;
import com.josdem.vetlog.service.LocaleService;
import com.josdem.vetlog.service.RestService;
import java.io.IOException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
@EnableConfigurationProperties(TemplateProperties.class)
public class EmailServiceImpl implements EmailService {

    @Value("${token}")
    private String clientToken;

    private final RestService restService;
    private final LocaleService localeService;
    private final TemplateProperties templateProperties;

    public void sendWelcomeEmail(User user) {
        log.info("Sending welcome email to: {}", user.getFirstName());
        if (!user.isEnabled()) {
            return;
        }
        try {
            var command = new MessageCommand();
            command.setEmail(user.getEmail());
            command.setName(user.getFirstName());
            command.setTemplate(templateProperties.getWelcome());
            command.setMessage(localeService.getMessage("user.welcome.message"));
            command.setToken(clientToken);
            restService.sendMessage(command);
        } catch (IOException ioe) {
            throw new BusinessException(ioe.getMessage());
        }
    }
}
