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

package com.josdem.vetlog.strategy;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import com.josdem.vetlog.enums.VaccinationStatus;
import com.josdem.vetlog.model.Pet;
import com.josdem.vetlog.model.Vaccination;
import com.josdem.vetlog.repository.VaccinationRepository;
import com.josdem.vetlog.strategy.vaccination.impl.CatVaccinationStrategy;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

@Slf4j
class CatVaccinationStrategyTest {

    private CatVaccinationStrategy catVaccinationStrategy;

    @Mock
    private VaccinationRepository vaccinationRepository;

    private final Pet pet = new Pet();

    @BeforeEach
    void setup() {
        MockitoAnnotations.openMocks(this);
        catVaccinationStrategy = new CatVaccinationStrategy(vaccinationRepository);
    }

    @DisplayName("saving vaccines")
    @ParameterizedTest
    @CsvSource({"9, 2", "12, 2", "13, 2", "16, 2", "23, 3"})
    void shouldVaccinatePet(int weeks, int times) {
        log.info("Running test: saving vaccines");
        pet.setBirthDate(LocalDateTime.now().minusWeeks(weeks));
        catVaccinationStrategy.vaccinate(pet);
        verify(vaccinationRepository, times(times))
                .save(new Vaccination(null, any(), LocalDate.now(), VaccinationStatus.PENDING, pet));
    }

    @Test
    @DisplayName("not saving vaccination due is not old enough")
    void shouldNotVaccinatePet(TestInfo testInfo) {
        log.info("Running test: {}", testInfo.getDisplayName());
        pet.setBirthDate(LocalDateTime.now().minusWeeks(1));
        catVaccinationStrategy.vaccinate(pet);
        verify(vaccinationRepository, never()).save(any(Vaccination.class));
    }
}
