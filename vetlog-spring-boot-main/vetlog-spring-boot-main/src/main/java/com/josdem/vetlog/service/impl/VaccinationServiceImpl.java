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

import com.josdem.vetlog.enums.PetType;
import com.josdem.vetlog.enums.VaccinationStatus;
import com.josdem.vetlog.exception.BusinessException;
import com.josdem.vetlog.model.Pet;
import com.josdem.vetlog.model.Vaccination;
import com.josdem.vetlog.repository.VaccinationRepository;
import com.josdem.vetlog.service.VaccinationService;
import com.josdem.vetlog.strategy.vaccination.VaccinationStrategy;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class VaccinationServiceImpl implements VaccinationService {

    private final VaccinationRepository vaccinationRepository;

    private final Map<PetType, VaccinationStrategy> vaccinationStrategies;

    @Override
    public void save(Pet pet) {
        Optional<VaccinationStrategy> strategy =
                Optional.ofNullable(vaccinationStrategies.get(pet.getBreed().getType()));
        if (strategy.isEmpty()) {
            throw new BusinessException("No vaccination strategy found for pet type: "
                    + pet.getBreed().getType());
        }
        strategy.get().vaccinate(pet);
    }

    @Override
    public List<Vaccination> getVaccinationsByPet(Pet pet) {
        return vaccinationRepository.findAllByPet(pet);
    }

    @Override
    public List<Vaccination> getVaccinesByStatus(Pet pet, VaccinationStatus status) {
        return getVaccinationsByPet(pet).stream()
                .filter(vaccination -> vaccination.getStatus().equals(status))
                .toList();
    }

    @Override
    public void deleteVaccinesByPet(Pet pet) {
        vaccinationRepository.deleteAllByPet(pet);
    }
}
