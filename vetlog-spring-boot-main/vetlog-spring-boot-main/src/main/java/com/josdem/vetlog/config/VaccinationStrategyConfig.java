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

import com.josdem.vetlog.enums.PetType;
import com.josdem.vetlog.strategy.vaccination.VaccinationStrategy;
import com.josdem.vetlog.strategy.vaccination.impl.CatVaccinationStrategy;
import com.josdem.vetlog.strategy.vaccination.impl.DogVaccinationStrategy;
import java.util.EnumMap;
import java.util.Map;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class VaccinationStrategyConfig {
    @Bean
    public Map<PetType, VaccinationStrategy> vaccinationStrategies(
            DogVaccinationStrategy dogVaccinationStrategy, CatVaccinationStrategy catVaccinationStrategy) {
        Map<PetType, VaccinationStrategy> strategies = new EnumMap<>(PetType.class);
        strategies.put(PetType.DOG, dogVaccinationStrategy);
        strategies.put(PetType.CAT, catVaccinationStrategy);
        return strategies;
    }
}
