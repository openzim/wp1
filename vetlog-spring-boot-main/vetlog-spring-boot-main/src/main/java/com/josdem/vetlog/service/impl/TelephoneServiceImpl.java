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

import com.josdem.vetlog.command.Command;
import com.josdem.vetlog.command.MessageCommand;
import com.josdem.vetlog.command.TelephoneCommand;
import com.josdem.vetlog.enums.PetStatus;
import com.josdem.vetlog.exception.BusinessException;
import com.josdem.vetlog.model.Pet;
import com.josdem.vetlog.model.User;
import com.josdem.vetlog.repository.PetRepository;
import com.josdem.vetlog.repository.UserRepository;
import com.josdem.vetlog.service.PetService;
import com.josdem.vetlog.service.RestService;
import com.josdem.vetlog.service.TelephoneService;
import java.io.IOException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class TelephoneServiceImpl implements TelephoneService {

    private final PetService petService;
    private final RestService restService;
    private final UserRepository userRepository;
    private final PetRepository petRepository;

    @Value("${token}")
    private String clientToken;

    @Value("${template.adoption.name}")
    private String adoptionTemplate;

    @Transactional
    public void save(Command command, User adopter) {
        var telephoneCommand = (TelephoneCommand) command;
        var pet = petService.getPetByUuid(telephoneCommand.getUuid());
        pet.setStatus(PetStatus.ADOPTED);
        adopter.setMobile(telephoneCommand.getMobile());
        pet.setAdopter(adopter);
        petRepository.save(pet);
        userRepository.save(adopter);
        createAdoptionDataMessage(pet);
    }

    private void createAdoptionDataMessage(Pet pet) {
        var owner = pet.getUser();
        var adopter = pet.getAdopter();
        var messageCommand = new MessageCommand();
        messageCommand.setEmail(owner.getEmail());
        messageCommand.setName(pet.getName());
        var sb = new StringBuilder();
        sb.append(adopter.getFirstName());
        sb.append(" ");
        sb.append(adopter.getLastName());
        messageCommand.setContactName(sb.toString());
        messageCommand.setEmailContact(adopter.getEmail());
        messageCommand.setMessage(adopter.getMobile());
        messageCommand.setToken(clientToken);
        messageCommand.setTemplate(adoptionTemplate);
        log.info("Command: " + messageCommand);
        try {
            restService.sendMessage(messageCommand);
        } catch (IOException ioe) {
            throw new BusinessException(ioe.getMessage());
        }
    }
}
