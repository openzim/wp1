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

import com.josdem.vetlog.binder.PetLogBinder;
import com.josdem.vetlog.command.Command;
import com.josdem.vetlog.command.PetLogCommand;
import com.josdem.vetlog.exception.BusinessException;
import com.josdem.vetlog.model.Pet;
import com.josdem.vetlog.model.PetLog;
import com.josdem.vetlog.repository.PetLogRepository;
import com.josdem.vetlog.repository.PetRepository;
import com.josdem.vetlog.service.PetLogService;
import com.josdem.vetlog.service.PetPrescriptionService;
import jakarta.transaction.Transactional;
import java.io.IOException;
import java.util.List;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class PetLogServiceImpl implements PetLogService {

    private final PetLogBinder petLogBinder;
    private final PetLogRepository petLogRepository;
    private final PetRepository petRepository;

    private final PetPrescriptionService petPrescriptionService;

    @Override
    @Transactional
    public PetLog save(Command command) throws IOException {
        var petLogCommand = (PetLogCommand) command;
        var petLog = petLogBinder.bind(petLogCommand);
        var pet = petRepository.findById(petLogCommand.getPet());
        if (pet.isEmpty()) {
            throw new BusinessException("No pet was found under id: " + petLogCommand.getPet());
        }
        petLog.setPet(pet.get());
        petPrescriptionService.attachFile(petLogCommand);
        log.info("petLog: {}", petLogCommand);
        petLogRepository.save(petLog);
        return petLog;
    }

    @Override
    public List<PetLog> getPetLogsByPet(Pet pet) {
        return petLogRepository.getAllByPet(pet);
    }
}
