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

import com.josdem.vetlog.command.AdoptionCommand;
import com.josdem.vetlog.command.Command;
import com.josdem.vetlog.enums.PetStatus;
import com.josdem.vetlog.model.PetAdoption;
import com.josdem.vetlog.repository.PetRepository;
import com.josdem.vetlog.service.AdoptionService;
import com.josdem.vetlog.service.PetService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AdoptionServiceImpl implements AdoptionService {

    private final PetService petService;
    private final PetRepository petRepository;

    public PetAdoption save(Command command) {
        var adoptionCommand = (AdoptionCommand) command;
        var pet = petService.getPetByUuid(adoptionCommand.getUuid());
        var petAdoption = new PetAdoption();
        petAdoption.setPet(pet);
        petAdoption.setDescription(adoptionCommand.getDescription());
        pet.setStatus(PetStatus.IN_ADOPTION);
        pet.setAdoption(petAdoption);
        petRepository.save(pet);
        return petAdoption;
    }
}
